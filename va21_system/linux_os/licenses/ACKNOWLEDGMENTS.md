# VA21 Research OS - Licenses and Acknowledgments

## Important Notice

VA21 Research OS incorporates several open-source projects. We are deeply grateful
to the developers and communities behind these projects. This document lists all
third-party software, their licenses, and acknowledgments.

**By using VA21 Research OS, you agree to comply with all applicable licenses
listed below.**

---

## VA21 Research OS License

**Copyright (c) 2024-2025 Prayaga Vaibhav. All rights reserved.**

VA21 Research OS is proprietary software. See the main LICENSE file for terms.

---

## Third-Party Software and Acknowledgments

### Operating System Base

#### Alpine Linux
- **Website:** https://alpinelinux.org/
- **License:** Various (MIT, GPL, BSD)
- **Description:** Lightweight Linux distribution used as the base OS
- **Acknowledgment:** Thank you to the Alpine Linux team for creating an incredibly
  efficient and secure Linux distribution.

#### BusyBox
- **Website:** https://busybox.net/
- **License:** GNU General Public License v2 (GPLv2)
- **Description:** Provides essential Unix utilities in a single binary
- **Acknowledgment:** Thank you to BusyBox developers for the Swiss Army knife of Linux.

---

### Security Components

#### ClamAV (Clam AntiVirus)
- **Website:** https://www.clamav.net/
- **License:** GNU General Public License v2 (GPLv2)
- **Copyright:** Copyright (C) 2007-2023 Cisco Systems, Inc.
- **Description:** Open-source antivirus engine for detecting trojans, viruses,
  malware & other malicious threats
- **Acknowledgment:** Thank you to the ClamAV team and Cisco for providing a
  free, open-source antivirus solution that helps protect users worldwide.

#### Guardian AI
- **License:** Proprietary (VA21)
- **Description:** AI-powered security monitoring developed for VA21

---

### Search and Research

#### SearXNG
- **Website:** https://docs.searxng.org/
- **License:** GNU Affero General Public License v3 (AGPL-3.0)
- **GitHub:** https://github.com/searxng/searxng
- **Description:** Privacy-respecting, hackable metasearch engine
- **Acknowledgment:** Thank you to the SearXNG community for building a
  privacy-first search solution. Your work enables secure research without
  sacrificing privacy.

---

### Knowledge Management

#### Obsidian (Inspiration)
- **Website:** https://obsidian.md/
- **Note:** VA21 uses an Obsidian-compatible format but does not include
  Obsidian software itself. Users can optionally sync with their own
  Obsidian installation.
- **Acknowledgment:** Thank you to the Obsidian team for pioneering the
  local-first, linked knowledge approach that inspired our vault system.

---

### Python Libraries

#### psutil
- **Website:** https://github.com/giampaolo/psutil
- **License:** BSD 3-Clause License
- **Copyright:** Copyright (c) 2009, Jay Loden, Dave Daeschler, Giampaolo Rodola
- **Description:** Cross-platform process and system monitoring
- **Acknowledgment:** Thank you to Giampaolo Rodola and contributors.

#### Rich
- **Website:** https://github.com/Textualize/rich
- **License:** MIT License
- **Copyright:** Copyright (c) 2020 Will McGugan
- **Description:** Beautiful terminal formatting
- **Acknowledgment:** Thank you to Will McGugan for making terminals beautiful.

#### prompt_toolkit
- **Website:** https://github.com/prompt-toolkit/python-prompt-toolkit
- **License:** BSD 3-Clause License
- **Copyright:** Copyright (c) 2014, Jonathan Slenders
- **Description:** Library for building interactive command lines
- **Acknowledgment:** Thank you to Jonathan Slenders.

#### PyYAML
- **Website:** https://pyyaml.org/
- **License:** MIT License
- **Copyright:** Copyright (c) 2017-2021 Ingy döt Net
- **Description:** YAML parser and emitter
- **Acknowledgment:** Thank you to the PyYAML team.

#### Requests
- **Website:** https://requests.readthedocs.io/
- **License:** Apache License 2.0
- **Copyright:** Copyright Kenneth Reitz
- **Description:** HTTP library for Python
- **Acknowledgment:** Thank you to Kenneth Reitz and contributors.

#### watchdog
- **Website:** https://github.com/gorakhargosh/watchdog
- **License:** Apache License 2.0
- **Copyright:** Copyright 2011 Yesudeep Mangalapilly
- **Description:** Filesystem event monitoring
- **Acknowledgment:** Thank you to Yesudeep Mangalapilly.

#### ONNX Runtime
- **Website:** https://onnxruntime.ai/
- **License:** MIT License
- **Copyright:** Copyright (c) Microsoft Corporation
- **Description:** Cross-platform inference accelerator
- **Acknowledgment:** Thank you to Microsoft and the ONNX community.

---

### Containerization

#### Docker
- **Website:** https://www.docker.com/
- **License:** Apache License 2.0
- **Description:** Container platform
- **Note:** Docker is optional; VA21 also supports Podman
- **Acknowledgment:** Thank you to Docker Inc.

#### Podman
- **Website:** https://podman.io/
- **License:** Apache License 2.0
- **Copyright:** Copyright Red Hat
- **Description:** Daemonless container engine
- **Acknowledgment:** Thank you to Red Hat and the Podman team.

---

### Text Adventure Inspiration

#### Zork
- **Original Creator:** Infocom (now part of Activision)
- **License:** N/A (Historical inspiration only)
- **Note:** VA21's text adventure interface is inspired by, but contains no code
  from, the classic Zork series.
- **Acknowledgment:** Thank you to the Infocom team for creating one of the most
  influential text adventures in computing history. Your work continues to inspire
  creative interfaces decades later.

---

## Full License Texts

### MIT License
```
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### BSD 3-Clause License
```
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

### Apache License 2.0
```
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

### GNU General Public License v2 (GPLv2)
```
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
```

### GNU Affero General Public License v3 (AGPL-3.0)
```
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```

---

## Special Thanks

We extend our heartfelt gratitude to:

1. **The Open Source Community** - For building the foundation that makes
   projects like VA21 possible.

2. **Security Researchers** - For their tireless work keeping systems safe.

3. **Privacy Advocates** - For championing user privacy and data protection.

4. **The Zork/Infocom Legacy** - For showing that interfaces can be both
   functional and imaginative.

5. **All Contributors** - Every person who has contributed code, documentation,
   bug reports, or ideas.

---

## Contact

For licensing inquiries, please contact the VA21 development team.

---

*Last Updated: December 2024*
*VA21 Research OS v1.0.0 (Vinayaka)*
