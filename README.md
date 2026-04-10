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
|   HTTPS_PROXY      |   可选。COROS 域名访问异常时使用的 HTTPS 代理   |  http://host:port  |
|    HTTP_PROXY      |   可选。与 HTTPS_PROXY 配套的 HTTP 代理   |  http://host:port  |
|     NO_PROXY       | 可选。不走代理的域名白名单 | localhost,127.0.0.1 |

## GARTH_TOKEN 说明
- 项目现在优先使用 `garth` 官方的 `GARTH_TOKEN` 会话串，而不是每次都用邮箱密码重新登录。
- 首次运行或 token 失效时，脚本会使用 `GARMIN_EMAIL` / `GARMIN_PASSWORD` 登录，然后把 `garth.client.dumps()` 生成的 `GARTH_TOKEN` 加密保存到 `db/garth_token.enc`。
- 后续运行会先读取 `db/garth_token.enc`，使用 `GARMIN_TOKEN_SALT` 解密，再通过 `garth.client.loads(...)` 恢复会话，尽量减少频繁密码登录带来的反爬风险。
- `db/garth_token.enc` 是密文文件，workflow 结束时会随仓库一起提交；`GARMIN_TOKEN_SALT` 必须配置为 GitHub Secret 或本地环境变量，且不要泄露。

### 本地直接生成 GARTH_TOKEN
- 如果只想在本地先生成并写入 `db/garth_token.enc`，可以先修改仓库根目录的 `.env.garmin.local`：

```bash
python scripts/garmin/generate_garth_token.py
```

- `.env.garmin.local` 默认内容如下：

```bash
GARMIN_AUTH_DOMAIN=COM
GARMIN_EMAIL=your_garmin_email
GARMIN_PASSWORD=your_garmin_password
GARMIN_TOKEN_SALT=your_token_salt
```

- 脚本会优先读取 `.env.garmin.local`，如果你额外设置了同名系统环境变量，则系统环境变量优先。
- 如果 `.env.garmin.local` 里配置了 `HTTPS_PROXY` / `HTTP_PROXY` / `NO_PROXY`，脚本也会一并注入到当前进程，`garth` 登录时会直接使用。
- 脚本会优先自动切到仓库自己的 `.venv/bin/python` 运行，所以本地直接执行下面这条即可：

```bash
python3 scripts/garmin/generate_garth_token.py
```

- 如需指定其他 env 文件，可以这样运行：

```bash
GARMIN_ENV_FILE=./your-custom.env python scripts/garmin/generate_garth_token.py
```

- 脚本会强制重新登录 Garmin，随后把新的加密 token 写入 `db/garth_token.enc`。

### 遇到 429 时改用浏览器登录生成 GARTH_TOKEN
- 如果 Garmin/Cloudflare 对脚本登录持续返回 `429`，可以改用浏览器引导登录：

```bash
.venv/bin/pip install playwright
.venv/bin/python -m playwright install chromium
python3 scripts/garmin/generate_garth_token_browser.py
```

- 脚本会打开 Chromium 浏览器，你在页面中手动完成 Garmin 登录和 MFA。
- 脚本现在会优先自动填写 `GARMIN_EMAIL` / `GARMIN_PASSWORD` 并尝试提交登录表单。
- 如果遇到验证码、短信/邮件 MFA、设备确认或其他风控页面，脚本会提示你人工接管；完成后它会继续等待并抓取 `serviceTicketId`。
- 登录成功后，脚本会抓取 `serviceTicketId`，再复用 `garth` 现有逻辑换取 OAuth token，并加密写入 `db/garth_token.enc`。
- 默认等待 300 秒；如果需要更长时间，可以这样运行：

```bash
GARMIN_BROWSER_TIMEOUT_SECONDS=600 python3 scripts/garmin/generate_garth_token_browser.py
```

### GitHub Actions 直接跑 Garmin 登录
- workflow 现在默认采用 `GARTH_TOKEN` 优先，失效时再走 headless Playwright 自动登录刷新 token。
- 需要在仓库 Secrets 中至少配置：`GARMIN_AUTH_DOMAIN`、`GARMIN_EMAIL`、`GARMIN_PASSWORD`、`GARMIN_TOKEN_SALT`、`COROS_EMAIL`、`COROS_PASSWORD`。
- workflow 会自动安装 Playwright 和 Chromium，并注入：

```bash
GARMIN_LOGIN_MODE=browser
GARMIN_BROWSER_HEADLESS=1
GARMIN_BROWSER_CI_MODE=1
```

- 在 GitHub Hosted runner 上，如果 Garmin 强制出现验证码、MFA 或额外确认页，job 会直接失败；这是无人值守 CI 的限制，不会等待人工接管。
- 为了降低风控概率，建议继续保留并提交 `db/garth_token.enc`，让 workflow 优先复用已有 token。

## COROS 代理说明
- 如果运行时访问 `*.coros.com` 出现 TLS 握手失败、`SSLEOFError`、`SSL_ERROR_SYSCALL` 等错误，可以为脚本或 GitHub Actions 配置 `HTTPS_PROXY` / `HTTP_PROXY`。
- 当前代码会自动读取这些环境变量，`CorosClient` 和 COROS OSS 凭证请求都会走代理。
- 在 GitHub Actions 中，可把 `HTTPS_PROXY`、`HTTP_PROXY`、`NO_PROXY` 配置为 Repository Secrets；workflow 已支持自动注入。

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
