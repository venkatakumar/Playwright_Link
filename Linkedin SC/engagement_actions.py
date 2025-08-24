import os
import asyncio
import random
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ActionConfig:
    dry_run: bool = os.getenv('ACTIONS_DRY_RUN', 'true').lower() == 'true'
    max_actions_per_run: int = int(os.getenv('MAX_ACTIONS_PER_RUN', '3'))
    min_delay: float = float(os.getenv('ACTION_MIN_DELAY', '2.0'))
    max_delay: float = float(os.getenv('ACTION_MAX_DELAY', '5.0'))


class EngagementBot:
    """Perform guarded engagement actions (connect, follow, message) with dry-run.

    All actions respect a per-run cap and human-like randomized delays to reduce risk.
    """

    def __init__(self, page, config: Optional[ActionConfig] = None):
        self.page = page
        self.config = config or ActionConfig()
        self.actions_performed = 0

    async def _wait(self):
        await asyncio.sleep(random.uniform(self.config.min_delay, self.config.max_delay))

    def _can_act(self) -> bool:
        return self.actions_performed < self.config.max_actions_per_run

    async def connect(self, profile_url: str) -> bool:
        if not self._can_act():
            return False
        if self.config.dry_run:
            self.actions_performed += 1
            return True
        try:
            await self.page.goto(profile_url, wait_until='domcontentloaded')
            await self._wait()
            # Try a few connect button selectors
            selectors = [
                'button[aria-label^="Connect"]',
                'button[aria-label*="Invite"]',
                'button[aria-label*="connection"]',
                'button[data-control-name*="connect"]',
                'button:has-text("Connect")',
            ]
            for sel in selectors:
                btn = await self.page.query_selector(sel)
                if btn:
                    await btn.click()
                    await self._wait()
                    # Optional send without note
                    send_sel = 'button[aria-label^="Send now"], button:has-text("Send")'
                    send_btn = await self.page.query_selector(send_sel)
                    if send_btn:
                        await send_btn.click()
                    self.actions_performed += 1
                    return True
            return False
        except Exception:
            return False

    async def follow(self, profile_url: str) -> bool:
        if not self._can_act():
            return False
        if self.config.dry_run:
            self.actions_performed += 1
            return True
        try:
            await self.page.goto(profile_url, wait_until='domcontentloaded')
            await self._wait()
            selectors = [
                'button[aria-label^="Follow"]',
                'button:has-text("Follow")',
            ]
            for sel in selectors:
                btn = await self.page.query_selector(sel)
                if btn:
                    await btn.click()
                    self.actions_performed += 1
                    return True
            return False
        except Exception:
            return False

    async def message(self, profile_url: str, text: str) -> bool:
        if not self._can_act():
            return False
        if self.config.dry_run:
            self.actions_performed += 1
            return True
        try:
            await self.page.goto(profile_url, wait_until='domcontentloaded')
            await self._wait()
            open_sel = [
                'a[aria-label^="Message"]',
                'button[aria-label^="Message"]',
                'button:has-text("Message")',
            ]
            opened = False
            for sel in open_sel:
                el = await self.page.query_selector(sel)
                if el:
                    await el.click()
                    opened = True
                    break
            if not opened:
                return False
            await self._wait()
            # Type into any message textarea/input
            area = await self.page.query_selector('div[role="textbox"], textarea')
            if not area:
                return False
            await area.type(text)
            await self._wait()
            # Send
            send_btn = await self.page.query_selector('button[aria-label^="Send"], button:has-text("Send")')
            if send_btn:
                await send_btn.click()
            self.actions_performed += 1
            return True
        except Exception:
            return False
