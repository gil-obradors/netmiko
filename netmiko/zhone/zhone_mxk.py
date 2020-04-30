"""Zhone MXK driver."""

import re
from netmiko.ssh_exception import NetmikoAuthenticationException
from paramiko import SSHClient
import time
from netmiko.cisco_base_connection import CiscoBaseConnection


class ZhoneMXK(CiscoBaseConnection):
    """ZhoneMXK Driver."""

    def session_preparation(self):
        """Prepare the session after the connection has been established."""
        self.ansi_escape_codes = True
        self._test_channel_read()
        self.set_base_prompt(pri_prompt_terminator=">", )
        # self.enable()  # Zhone hasn't got ENABLE MODE
        self.disable_paging(command="setline 0")
        # Clear the read buffer
        time.sleep(0.3 * self.global_delay_factor)
        self.clear_buffer()

    def enable(self, *args, **kwargs):
        """No enable mode"""
        pass

    def config_mode(self, *args, **kwargs):
        """Enter configuration mode."""
        pass

    def exit_config_mode(self, *args, **kwargs):
        """Exit configuration mode."""
        pass

    def check_config_mode(self, *args, **kwargs):
        """Zhone has no enable mode."""
        pass

    def check_enable_mode(self, *args, **kwargs):
        """Zhone has no enable mode."""
        pass

    def exit_enable_mode(self, *args, **kwargs):
        """Zhone has no enable mode."""
        pass

    def save_config(self, *args, **kwargs):
        """Zhone has no save config"""
        pass


class ZhoneMXK219Telnet(ZhoneMXK):
    """Dell PowerConnect Telnet Driver."""

    def telnet_login(
            self,
            pri_prompt_terminator=r">\s*$",
            alt_prompt_terminator=r"]\s*$",
            username_pattern=r"(?:user:|username|login|user name)",
            pwd_pattern=r"assword",
            delay_factor=1,
            max_loops=5,
    ):
        """Telnet login for Huawei Devices"""

        delay_factor = self.select_delay_factor(delay_factor)
        combined_pattern = r"({}|{})".format(
            pri_prompt_terminator, alt_prompt_terminator
        )

        output = ""
        return_msg = ""
        i = 1
        while i <= max_loops:
            try:
                # Search for username pattern / send username
                output = self.read_until_pattern(
                    pattern=username_pattern, re_flags=re.I
                )
                return_msg += output
                self.write_channel(self.username + self.TELNET_RETURN)

                # Search for password pattern / send password
                output = self.read_until_pattern(pattern=pwd_pattern, re_flags=re.I)
                return_msg += output
                self.write_channel(self.password + self.TELNET_RETURN)

                # Waiting for combined output
                output = self.read_until_pattern(pattern=combined_pattern)
                return_msg += output

                # Check if proper data received
                if re.search(pri_prompt_terminator, output, flags=re.M) or re.search(
                        alt_prompt_terminator, output, flags=re.M
                ):
                    return return_msg

                self.write_channel(self.TELNET_RETURN)
                time.sleep(0.5 * delay_factor)
                i += 1

            except EOFError:
                self.remote_conn.close()
                msg = f"Login failed: {self.host}"
                raise NetmikoAuthenticationException(msg)

        # Last try to see if we already logged in
        self.write_channel(self.TELNET_RETURN)
        time.sleep(0.5 * delay_factor)
        output = self.read_channel()
        return_msg += output
        if re.search(pri_prompt_terminator, output, flags=re.M) or re.search(
                alt_prompt_terminator, output, flags=re.M
        ):
            return return_msg

        self.remote_conn.close()
        msg = f"Login failed: {self.host}"
        raise NetmikoAuthenticationException(msg)

class ZHoneMXK219SSH(ZhoneMXK):
    pass
