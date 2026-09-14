import { Cesium3DTileset, CesiumTerrainProvider, Resource } from "cesium";
import { DISPLAY_TERRAIN } from "./displayScene.mjs";

// Resource.createIfNeeded clones its input, including on nested loads. Keep
// the reviewed root through those clones without changing global Cesium APIs.
export class VerifiedRootResource extends Resource {
  constructor(url, rootUrl, root) { super({ url }); this.rootUrl = rootUrl; this.verifiedRoot = root; }
  clone(result) {
    const target = result instanceof VerifiedRootResource ? result : new VerifiedRootResource(this.url, this.rootUrl, this.verifiedRoot);
    target.rootUrl = this.rootUrl;
    target.verifiedRoot = this.verifiedRoot;
    return super.clone(target);
  }
  fetchJson() {
    return this.url === this.rootUrl ? Promise.resolve(structuredClone(this.verifiedRoot)) : super.fetchJson();
  }
}

export async function loadTilesetForSession(config, { signal, isActive, fetchImpl = fetch, createTileset = Cesium3DTileset.fromUrl } = {}) {
  let resource = config.tileset_url;
  if (config.root_sha256) {
    const response = await fetchImpl(config.tileset_url, { signal });
    if (!response.ok || response.url !== config.tileset_url) throw new Error("PLATEAU root HTTP/final URL mismatch");
    const bytes = await response.arrayBuffer();
    const hash = Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", bytes)), (value) => value.toString(16).padStart(2, "0")).join("");
    if (hash !== config.root_sha256 || bytes.byteLength !== config.root_bytes) throw new Error("PLATEAU root changed since reviewed receipt; revalidation required");
    const root = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(bytes));
    resource = new VerifiedRootResource(config.tileset_url, config.tileset_url, root);
  }
  if (!isActive()) throw new Error("PLATEAU request no longer active");
  const tileset = await createTileset(resource, { maximumScreenSpaceError: 16, cacheBytes: 128 * 1024 * 1024 });
  if (!isActive()) {
    if (!tileset.isDestroyed()) tileset.destroy();
    throw new Error("PLATEAU request no longer active");
  }
  return tileset;
}

export async function loadTerrainForSession({ signal, isActive, fetchImpl = fetch, createTerrain = CesiumTerrainProvider.fromUrl }) {
  const rootUrl = `${DISPLAY_TERRAIN.url}/layer.json`;
  const response = await fetchImpl(rootUrl, { signal });
  if (!response.ok || response.url !== rootUrl) throw new Error("表示terrain metadata HTTP/final URL不一致");
  const bytes = await response.arrayBuffer();
  const hash = Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", bytes)), (v) => v.toString(16).padStart(2, "0")).join("");
  if (hash !== DISPLAY_TERRAIN.metadata_sha256 || bytes.byteLength !== DISPLAY_TERRAIN.metadata_bytes) throw new Error("表示terrain metadata更新を検出: 再検証まで2Dを使用します");
  if (!isActive()) throw new Error("表示terrain session終了済み");
  const root = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(bytes));
  const provider = await createTerrain(new VerifiedRootResource(`${DISPLAY_TERRAIN.url}/`, rootUrl, root), { requestVertexNormals: true, credit: DISPLAY_TERRAIN.credit });
  if (!isActive()) throw new Error("表示terrain session終了済み");
  return provider;
}
