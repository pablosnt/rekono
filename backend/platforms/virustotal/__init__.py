"""Integration with the VirusTotal threat intelligence platform.

VirusTotal says whether a host is known to be malicious and who owns its address,
so only the hosts with a public IP are sent to it: the addresses and the names of
a private network can't leave the organization that Rekono is scanning.
"""
