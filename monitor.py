monitor
succeeded 1 minute ago in 11s
Search logs
1s
Current runner version: '2.332.0'
Runner Image Provisioner
Operating System
Runner Image
GITHUB_TOKEN Permissions
Secret source: Actions
Prepare workflow directory
Prepare all required actions
Getting action download info
Download action repository 'actions/checkout@v4' (SHA:34e114876b0b11c390a56381ad16ebd13914f8d5)
Download action repository 'actions/setup-python@v5' (SHA:a26af69be951a213d495a4c3e4e4022e16d87065)
Complete job name: monitor
0s
Run actions/checkout@v4
Syncing repository: roystontyk/NSW_Building_News
Getting Git version info
Temporarily overriding HOME='/home/runner/work/_temp/d33c20fa-fdaa-4af4-9655-35e17222588a' before making global git config changes
Adding repository directory to the temporary git global config as a safe directory
/usr/bin/git config --global --add safe.directory /home/runner/work/NSW_Building_News/NSW_Building_News
Deleting the contents of '/home/runner/work/NSW_Building_News/NSW_Building_News'
Initializing the repository
Disabling automatic garbage collection
Setting up auth
Fetching the repository
Determining the checkout info
/usr/bin/git sparse-checkout disable
/usr/bin/git config --local --unset-all extensions.worktreeConfig
Checking out the ref
/usr/bin/git log -1 --format=%H
aa813bf777710fbfc733dc007047cbfaa90c5468
1s
Run actions/setup-python@v5
Installed versions
1s
Run pip install requests beautifulsoup4
Collecting requests
  Downloading requests-2.32.5-py3-none-any.whl.metadata (4.9 kB)
Collecting beautifulsoup4
  Downloading beautifulsoup4-4.14.3-py3-none-any.whl.metadata (3.8 kB)
Collecting charset_normalizer<4,>=2 (from requests)
  Downloading charset_normalizer-3.4.5-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (39 kB)
Collecting idna<4,>=2.5 (from requests)
  Downloading idna-3.11-py3-none-any.whl.metadata (8.4 kB)
Collecting urllib3<3,>=1.21.1 (from requests)
  Downloading urllib3-2.6.3-py3-none-any.whl.metadata (6.9 kB)
Collecting certifi>=2017.4.17 (from requests)
  Downloading certifi-2026.2.25-py3-none-any.whl.metadata (2.5 kB)
Collecting soupsieve>=1.6.1 (from beautifulsoup4)
  Downloading soupsieve-2.8.3-py3-none-any.whl.metadata (4.6 kB)
Collecting typing-extensions>=4.0.0 (from beautifulsoup4)
  Downloading typing_extensions-4.15.0-py3-none-any.whl.metadata (3.3 kB)
Downloading requests-2.32.5-py3-none-any.whl (64 kB)
Downloading charset_normalizer-3.4.5-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (193 kB)
Downloading idna-3.11-py3-none-any.whl (71 kB)
Downloading urllib3-2.6.3-py3-none-any.whl (131 kB)
Downloading beautifulsoup4-4.14.3-py3-none-any.whl (107 kB)
Downloading certifi-2026.2.25-py3-none-any.whl (153 kB)
Downloading soupsieve-2.8.3-py3-none-any.whl (37 kB)
Downloading typing_extensions-4.15.0-py3-none-any.whl (44 kB)
Installing collected packages: urllib3, typing-extensions, soupsieve, idna, charset_normalizer, certifi, requests, beautifulsoup4

Successfully installed beautifulsoup4-4.14.3 certifi-2026.2.25 charset_normalizer-3.4.5 idna-3.11 requests-2.32.5 soupsieve-2.8.3 typing-extensions-4.15.0 urllib3-2.6.3
5s
Run python monitor.py
📝 [LOG] 🚀 NSW Scraper Started
📝 [LOG] 🔍 Scraping: https://www.nsw.gov.au/departments-and-agencies/building-commission/news
📝 [LOG] 🔍 Scraping: https://www.nsw.gov.au/departments-and-agencies/building-commission/register-of-building-work-orders
📝 [LOG] ⚠️ No new content found.
0s
Post job cleanup.
1s
Post job cleanup.
/usr/bin/git version
git version 2.53.0
Temporarily overriding HOME='/home/runner/work/_temp/7e594549-ac8e-4327-8506-9c6f23fb6f98' before making global git config changes
Adding repository directory to the temporary git global config as a safe directory
/usr/bin/git config --global --add safe.directory /home/runner/work/NSW_Building_News/NSW_Building_News
/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
http.https://github.com/.extraheader
/usr/bin/git config --local --unset-all http.https://github.com/.extraheader
/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
0s
Cleaning up orphan processes
