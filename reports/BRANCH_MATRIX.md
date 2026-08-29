# Overnight branch and worktree matrix

Integration base: `cbb71020da0e52f809445e88e84f0c294ec973cc`
Integration branch: `integration/overnight-multicity-20260830`

| Lane | Branch / worktree | Lane commit | Integrated commit | Result |
|---|---|---|---|---|
| CI / lifecycle | `task/overnight-ci-harness` | `acff50e0d6f9fcd6acf0b09ed5947943acacf083` | `38177638858ecd6d6f860349fc23a5a2c4874c6e` | Integrated |
| Hokonavi contract | `task/hokonavi-2024-contract` | `75ca1efe018bd733225700c6ab3e4c9ed786f95e` | `00c8217f166cd6426bafe64d8f813820a0e2569a` | Integrated |
| Shared hazards | `task/overnight-core-hazards` | `d9515048` and `6a902372d7e2356bd36e85639e0c6bb39812f1a2` | `d917c91c0b9af895e3b56b75469dacaa2ae84f83` and `f572bc592f8f2516cbd82cfd482b679c50392a03` | Integrated |
| 清水 | `task/city-kyoto-kiyomizu` | `b090288cbffe7ac36f6cc9d7187ee516ce415e51` | `ab5974f58c5eb3f2b3388c4c9a15d7fbc1c6e135` | Integrated |
| 嵐山 | `task/city-kyoto-arashiyama` | `22c2210296e346c24667ecb39721af1e69de9e8d` | `4759b1e456774f6228639f304de9d084db649316` | Integrated |
| 藤沢 | `task/city-fujisawa-enoshima` | `e3f0aa184bf551264e9692795d9f0f73eb3fd8eb` | `8fae1c2fc1fcc631708df3ede5fb0014b4970a8f` | Integrated |
| Shared 2D UI | `task/ui-multicity-static` | `da287049d8337fd1ea6eef07e8337425b53f0490` | `fb296124e9cd53db6721d58033a9712d07653bb1` | Integrated |
| Cross-lane integration | integration worktree | n/a | `e3c0d03a07c06c5e99af028dd482384f57ff1c6d` | Integrated |
| Prior Kyoto staging | `task/kyoto-official-data-staging` | `557ad9c768f56cdd78600252dd7379436a3386ba` | none | Kept separate: overlapping staging contract is not consumed by this run's shared city-pack/UI path; branch was not changed or deleted |

All lane worktrees were left intact. No lane branch was rebased, force-pushed, deleted, or merged to `main`.
