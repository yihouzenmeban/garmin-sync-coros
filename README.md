# 如果出现无法同步请检查下代码是否最新如果非最新请重新fork sync代码后删除db/garmin.db文件重跑一遍！！！
## 致谢
- 本脚本佳明模块代码来自@[yihong0618](https://github.com/yihong0618) 的 [running_page](https://github.com/yihong0618/running_page) 个人跑步主页项目,在此非常感谢@[yihong0618](https://github.com/yihong0618)大佬的无私奉献！！！

## 注意
由于高驰平台只允许单设备登录，同步期间如果打开网页会影响到数据同步导致同步失败，同步期间切记不要打开网页。

## 参数配置
|       参数名       |                备注                |        案例        |
| :----------------: | :--------------------------------: | :----------------: |
|    GARMIN_EMAIL    |          佳明登录帐号邮箱          |                    |
|  GARMIN_PASSWORD   |            佳明登录密码            |                    |
| GARMIN_TOKEN_SALT | 用于加密 `GARTH_TOKEN` 的密钥材料 |                    |
| GARMIN_AUTH_DOMAIN | 佳明区域（国际区填:COM 国区填:CN） |    (COM or CN)     |
| GARMIN_NEWEST_NUM  |            最新记录条数            | (默认0，可写大于0) |
|    COROS_EMAIL     |           高驰 登录邮箱            |                    |
|   COROS_PASSWORD   |             高驰 密码              |                    |

## GARTH_TOKEN 说明
- 项目现在优先使用 `garth` 官方的 `GARTH_TOKEN` 会话串，而不是每次都用邮箱密码重新登录。
- 首次运行或 token 失效时，脚本会使用 `GARMIN_EMAIL` / `GARMIN_PASSWORD` 登录，然后把 `garth.client.dumps()` 生成的 `GARTH_TOKEN` 加密保存到 `db/garth_token.enc`。
- 后续运行会先读取 `db/garth_token.enc`，使用 `GARMIN_TOKEN_SALT` 解密，再通过 `garth.client.loads(...)` 恢复会话，尽量减少频繁密码登录带来的反爬风险。
- `db/garth_token.enc` 是密文文件，workflow 结束时会随仓库一起提交；`GARMIN_TOKEN_SALT` 必须配置为 GitHub Secret 或本地环境变量，且不要泄露。

## garth 升级价值
- `garth` 已从 `0.4.38` 升级到 `0.7.10`。
- 升级区间内 `garth` 增强了 `GARTH_TOKEN`/`GARTH_HOME` 会话恢复机制，并连续修复了 Garmin SSO、Cloudflare、cookie 继承和 `Client app validation failed` 等登录相关问题。
- `0.7.10` 还补充了动态 MFA method 支持，对当前 Garmin 登录链路更友好。

## Github配置步骤
### 1.参数配置
打开**Setting**
![打开Setting](doc/3451692931372_.pic.jpg)
找到**Secrets and variables**点击**New repository secret**按钮
![Secrets and variables](/doc/3461692931472_.pic.jpg)
打开**New repository secret**后将上述的参数填入，下图以佳明帐号为例,**Name**填写参数名,**Secret**填写你的信息。至少需要补齐 Garmin 与 Coros 的登录参数，并新增 `GARMIN_TOKEN_SALT` 用于加密 `GARTH_TOKEN`。
![填入参数](doc/3471692931624_.pic.jpg)

### 2.配置WorkFlow权限
打开**Setting**找到**Actions**点击**General**按钮,按照下图勾选并save
![配置WorkFlow权限](doc/3481692931856_.pic.jpg)

### 3. wrokflow配置
打开**github/workflows/garmin-sync-coros.yml**文件,将**GITHUB_NAME**更改为你的Github用户名、**GITHUB_EMAIL**更改为你的Github登录邮箱，更改步骤如下:
![更改步骤](doc/3491692932110_.pic.jpg)
更改完成后点击右上角**Commit changes...**提交即可
![Commit](doc/3501692932345_.pic.jpg)

## 重新fork项目步骤
点击页面上**Sync Frok**然后点击**Dicard commit**即可
![fork sync](doc/image.png)
## 删除db步骤
按照图片顺序执行即可
![alt text](doc/image5.png)
![alt text](doc/image-1.png)
![alt text](doc/image-2.png)
![alt text](doc/image-3.png)
![alt text](doc/image-4.png)
删除完后等脚本自己执行即可
