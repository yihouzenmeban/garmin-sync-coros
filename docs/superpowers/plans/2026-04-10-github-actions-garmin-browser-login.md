# GitHub Actions Garmin Browser Login Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 GitHub Actions 在 `GARTH_TOKEN` 不可恢复时，使用 headless Playwright 自动登录 Garmin 并刷新加密 token，再继续同步流程。

**Architecture:** 保持现有 `GARTH_TOKEN` 优先策略不变，只在 token 恢复失败后按环境变量切换到浏览器登录。浏览器登录脚本补充 headless/CI 开关，CI 模式下遇到 MFA、验证码或确认页直接失败，不再等待人工接管。

**Tech Stack:** Python 3.14, Playwright sync API, unittest, GitHub Actions

---

### Task 1: Browser Login Mode Red Tests

**Files:**
- Modify: `scripts/tests/garmin/test_garmin_client.py`
- Test: `scripts/tests/garmin/test_garmin_client.py`

- [ ] **Step 1: Write the failing test**

```python
def test_ensure_login_uses_browser_refresh_when_browser_mode_enabled(self):
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest scripts.tests.garmin.test_garmin_client.GarminClientLoginTest.test_ensure_login_uses_browser_refresh_when_browser_mode_enabled -v`
Expected: FAIL because `GarminClient.ensure_login()` still falls back to password login.

- [ ] **Step 3: Write minimal implementation**

```python
if self._should_use_browser_login():
    self._login_with_browser()
else:
    self._login_with_password()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest scripts.tests.garmin.test_garmin_client.GarminClientLoginTest.test_ensure_login_uses_browser_refresh_when_browser_mode_enabled -v`
Expected: PASS

### Task 2: CI Browser Flow Red Tests

**Files:**
- Modify: `scripts/tests/garmin/test_generate_garth_token_browser.py`
- Test: `scripts/tests/garmin/test_generate_garth_token_browser.py`

- [ ] **Step 1: Write the failing test**

```python
def test_capture_service_ticket_fails_fast_on_manual_takeover_in_ci(self):
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest scripts.tests.garmin.test_generate_garth_token_browser.GenerateGarthTokenBrowserScriptTest.test_capture_service_ticket_fails_fast_on_manual_takeover_in_ci -v`
Expected: FAIL because CI mode still waits for manual takeover.

- [ ] **Step 3: Write minimal implementation**

```python
if ci_mode and requires_manual_takeover(page):
    raise RuntimeError(...)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest scripts.tests.garmin.test_generate_garth_token_browser.GenerateGarthTokenBrowserScriptTest.test_capture_service_ticket_fails_fast_on_manual_takeover_in_ci -v`
Expected: PASS

### Task 3: Workflow and Headless Wiring

**Files:**
- Modify: `scripts/garmin/generate_garth_token_browser.py`
- Modify: `.github/workflows/garmin-sync-coros.yml`
- Modify: `.github/workflows/coros-sync-garmin.yml`
- Modify: `README.md`

- [ ] **Step 1: Add headless and CI env handling**

```python
options["headless"] = env_truthy("GARMIN_BROWSER_HEADLESS") or env_truthy("CI")
```

- [ ] **Step 2: Update workflows**

Run: no command
Expected: workflows install Playwright/Chromium, use `secrets.*`, and set CI browser env vars.

- [ ] **Step 3: Run relevant tests**

Run: `python3 -m unittest scripts.tests.garmin.test_garmin_client scripts.tests.garmin.test_generate_garth_token_browser -v`
Expected: PASS
