# Garmin Browser Auto Login Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让浏览器登录脚本优先自动填写 Garmin 账号密码并尝试提交，遇到验证码或 MFA 时切换到人工接管，再继续抓取 `serviceTicketId` 生成加密 `GARTH_TOKEN`。

**Architecture:** 保持现有 `ticket -> OAuth1 -> OAuth2 -> GARTH_TOKEN` 链路不变，只增强浏览器交互层。浏览器层增加页面状态识别、自动动作执行和人工接管等待，尽量用多候选选择器和文本信号识别常见登录页面。

**Tech Stack:** Python 3, Playwright sync API, unittest

---

### Task 1: Browser Flow Red Tests

**Files:**
- Modify: `scripts/tests/garmin/test_generate_garth_token_browser.py`
- Test: `scripts/tests/garmin/test_generate_garth_token_browser.py`

- [ ] **Step 1: Write the failing test**

```python
def test_browser_login_autofills_credentials_before_waiting_for_ticket(self):
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest scripts.tests.garmin.test_generate_garth_token_browser.GenerateGarthTokenBrowserScriptTest.test_browser_login_autofills_credentials_before_waiting_for_ticket -v`
Expected: FAIL because browser flow does not yet autofill credentials.

- [ ] **Step 3: Write minimal implementation**

```python
def capture_service_ticket(...):
    # Inspect login page and fill credentials before polling for ticket.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest scripts.tests.garmin.test_generate_garth_token_browser.GenerateGarthTokenBrowserScriptTest.test_browser_login_autofills_credentials_before_waiting_for_ticket -v`
Expected: PASS

### Task 2: Manual Takeover Red Tests

**Files:**
- Modify: `scripts/tests/garmin/test_generate_garth_token_browser.py`
- Test: `scripts/tests/garmin/test_generate_garth_token_browser.py`

- [ ] **Step 1: Write the failing test**

```python
def test_browser_login_stops_automation_when_mfa_detected(self):
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest scripts.tests.garmin.test_generate_garth_token_browser.GenerateGarthTokenBrowserScriptTest.test_browser_login_stops_automation_when_mfa_detected -v`
Expected: FAIL because browser flow does not yet switch cleanly to manual takeover mode.

- [ ] **Step 3: Write minimal implementation**

```python
def is_manual_step_required(...):
    return True
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest scripts.tests.garmin.test_generate_garth_token_browser.GenerateGarthTokenBrowserScriptTest.test_browser_login_stops_automation_when_mfa_detected -v`
Expected: PASS

### Task 3: Continue Page Red Tests

**Files:**
- Modify: `scripts/tests/garmin/test_generate_garth_token_browser.py`
- Test: `scripts/tests/garmin/test_generate_garth_token_browser.py`

- [ ] **Step 1: Write the failing test**

```python
def test_browser_login_clicks_continue_buttons_before_manual_takeover(self):
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest scripts.tests.garmin.test_generate_garth_token_browser.GenerateGarthTokenBrowserScriptTest.test_browser_login_clicks_continue_buttons_before_manual_takeover -v`
Expected: FAIL because browser flow does not yet advance through continue/accept pages.

- [ ] **Step 3: Write minimal implementation**

```python
def click_common_continue_buttons(...):
    ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest scripts.tests.garmin.test_generate_garth_token_browser.GenerateGarthTokenBrowserScriptTest.test_browser_login_clicks_continue_buttons_before_manual_takeover -v`
Expected: PASS

### Task 4: Docs Update

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update browser login usage notes**

```md
- 脚本会优先自动填写 Garmin 账号密码并尝试登录。
- 如果遇到验证码、短信/邮件 MFA 或其他确认页，会提示人工接管。
```

- [ ] **Step 2: Run targeted tests**

Run: `python3 -m unittest scripts.tests.garmin.test_generate_garth_token_browser -v`
Expected: PASS

- [ ] **Step 3: Run related Garmin tests**

Run: `python3 -m unittest scripts.tests.garmin.test_generate_garth_token scripts.tests.garmin.test_generate_garth_token_browser -v`
Expected: PASS
