# VA21 Research OS - Licenses and Acknowledgments

## Important Notice

VA21 Research OS incorporates several open-source projects and AI technologies. We are deeply grateful
to the developers, researchers, and communities behind these projects. This document lists all
third-party software, their licenses, and acknowledgments.

**By using VA21 Research OS, you agree to comply with all applicable licenses
listed below.**

*Om Vinayaka - With gratitude to all who make this possible.*

---

## VA21 Research OS License

**Copyright (c) 2024-2025 Prayaga Vaibhav. All rights reserved.**

VA21 Research OS is proprietary software. See the main LICENSE file for terms.

---

## AI and Machine Learning

### IBM Granite Language Models

- **Website:** https://www.ibm.com/granite
- **Hugging Face:** https://huggingface.co/collections/ibm-granite/granite-40-language-models
- **License:** Apache License 2.0
- **Copyright:** Copyright IBM Corporation 2024-2025
- **Models Used:**
  - Granite 4.0 Maverick Micro (3B) - Ultra-light hybrid model for concurrent agents
  - Granite 4.0 Dense 2B/8B - Efficient dense models
  - Granite 4.0 Hybrid MoE - Mixture-of-Experts for specialized tasks
- **Description:** IBM Granite is a family of enterprise-grade AI models designed for
  business applications, featuring strong performance with responsible AI principles.
- **Acknowledgment:** We extend our sincere gratitude to **IBM Research** and the
  **IBM Granite team** for developing and open-sourcing these exceptional language models.
  The Granite models power VA21's intelligent assistance, coding support, and reasoning
  capabilities. Thank you for advancing AI accessibility and enterprise-ready solutions.

### Microsoft ONNX Runtime

- **Website:** https://onnxruntime.ai/
- **GitHub:** https://github.com/microsoft/onnxruntime
- **License:** MIT License
- **Copyright:** Copyright (c) Microsoft Corporation. All rights reserved.
- **Description:** ONNX Runtime is a cross-platform inference and training accelerator
  compatible with PyTorch, TensorFlow/Keras, and other popular frameworks.
- **Acknowledgment:** Thank you to **Microsoft** and the **ONNX Runtime team** for
  creating an exceptional inference engine that powers VA21's Guardian AI security
  core. ONNX Runtime enables efficient, cross-platform AI inference.

### Microsoft FARA (Federated Agentic Reasoning Architecture)

- **Website:** https://www.microsoft.com/en-us/research/blog/fara-7b-an-efficient-agentic-model-for-computer-use/
- **GitHub:** https://github.com/microsoft/fara
- **Hugging Face:** https://huggingface.co/microsoft/Fara-7B
- **License:** MIT License
- **Copyright:** Copyright (c) Microsoft Corporation. All rights reserved.
- **Description:** FARA is Microsoft's agentic small language model designed as a
  Computer Use Agent (CUA). It automates desktop and web interaction by interpreting
  screenshots and mimicking human actions.
- **Acknowledgment:** We are deeply grateful to **Microsoft Research** for developing
  and open-sourcing FARA technology. The FARA-inspired compatibility layer in VA21
  enables seamless integration with legacy applications through intelligent UI
  automation. This groundbreaking research enables AI agents to interact with any
  application interface.

### Microsoft Phi Models

- **Website:** https://azure.microsoft.com/en-us/blog/introducing-phi-3-redefining-whats-possible-with-slms/
- **Hugging Face:** https://huggingface.co/microsoft/phi-3-mini-4k-instruct
- **License:** MIT License
- **Copyright:** Copyright (c) Microsoft Corporation. All rights reserved.
- **Description:** Phi-3 is Microsoft's family of small language models (SLMs)
  optimized for edge and mobile scenarios.
- **Acknowledgment:** Thank you to **Microsoft** for the Phi family of models,
  which provide efficient local inference capabilities.

### Meta LLaMA Models

- **Website:** https://llama.meta.com/
- **License:** Llama 3 Community License Agreement
- **Copyright:** Copyright (c) Meta Platforms, Inc. All rights reserved.
- **Description:** LLaMA (Large Language Model Meta AI) family of foundation models.
- **Acknowledgment:** Thank you to **Meta AI** for open-sourcing the LLaMA models,
  enabling advanced language understanding capabilities.

### ONNX (Open Neural Network Exchange)

- **Website:** https://onnx.ai/
- **GitHub:** https://github.com/onnx/onnx
- **License:** Apache License 2.0
- **Copyright:** Copyright (c) ONNX Project Contributors
- **Description:** Open standard for machine learning interoperability.
- **Acknowledgment:** Thank you to the **ONNX community** including contributors from
  Microsoft, Facebook, Amazon, and many others for creating an open ecosystem
  for AI model exchange.

### Hugging Face Transformers

- **Website:** https://huggingface.co/
- **GitHub:** https://github.com/huggingface/transformers
- **License:** Apache License 2.0
- **Copyright:** Copyright 2018- The Hugging Face team. All rights reserved.
- **Description:** State-of-the-art Machine Learning for PyTorch, TensorFlow, and JAX.
- **Acknowledgment:** Thank you to **Hugging Face** for democratizing AI and
  providing the infrastructure that makes AI accessible to everyone.

### Ollama

- **Website:** https://ollama.ai/
- **GitHub:** https://github.com/ollama/ollama
- **License:** MIT License
- **Copyright:** Copyright (c) Ollama
- **Description:** Get up and running with large language models locally.
- **Acknowledgment:** Thank you to the **Ollama team** for making local LLM
  deployment simple and accessible.

---

## Third-Party Software and Acknowledgments

### Operating System Base

#### Debian GNU/Linux
- **Website:** https://www.debian.org/
- **License:** Various (primarily GPL, LGPL, BSD)
- **Description:** The Universal Operating System - rock-solid foundation for VA21
- **Acknowledgment:** Thank you to the **Debian Project** and the thousands of
  volunteers who maintain the most stable and versatile Linux distribution.

#### Alpine Linux
- **Website:** https://alpinelinux.org/
- **License:** Various (MIT, GPL, BSD)
- **Description:** Lightweight Linux distribution used for containers
- **Acknowledgment:** Thank you to the Alpine Linux team for creating an incredibly
  efficient and secure Linux distribution.

#### BusyBox
- **Website:** https://busybox.net/
- **License:** GNU General Public License v2 (GPLv2)
- **Description:** Provides essential Unix utilities in a single binary
- **Acknowledgment:** Thank you to BusyBox developers for the Swiss Army knife of Linux.

#### Linux Kernel
- **Website:** https://www.kernel.org/
- **License:** GNU General Public License v2 (GPLv2)
- **Copyright:** Copyright Linus Torvalds and contributors
- **Acknowledgment:** Thank you to **Linus Torvalds** and the Linux kernel
  developers for creating the foundation of modern computing.

---

### Package Management

#### Flatpak
- **Website:** https://flatpak.org/
- **GitHub:** https://github.com/flatpak/flatpak
- **License:** LGPL-2.1-or-later
- **Description:** Linux application sandboxing and distribution framework
- **Acknowledgment:** Thank you to the **Flatpak team** for revolutionizing
  Linux application distribution with sandboxed, portable apps.

#### Flathub
- **Website:** https://flathub.org/
- **License:** Various (per application)
- **Description:** The home of Flatpak applications
- **Acknowledgment:** Thank you to **Flathub** for providing a central
  repository of quality Linux applications.

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

#### Flask
- **Website:** https://flask.palletsprojects.com/
- **License:** BSD 3-Clause License
- **Copyright:** Copyright 2010 Pallets
- **Acknowledgment:** Thank you to the Pallets team for Flask.

#### Flask-SocketIO
- **Website:** https://flask-socketio.readthedocs.io/
- **License:** MIT License
- **Copyright:** Copyright (c) Miguel Grinberg
- **Acknowledgment:** Thank you to Miguel Grinberg.

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

#### PyTorch
- **Website:** https://pytorch.org/
- **License:** BSD 3-Clause License
- **Copyright:** Copyright (c) Meta Platforms, Inc. and affiliates
- **Description:** Deep learning framework
- **Acknowledgment:** Thank you to Meta AI and the PyTorch team.

---

### JavaScript/Frontend

#### React
- **Website:** https://react.dev/
- **License:** MIT License
- **Copyright:** Copyright (c) Meta Platforms, Inc. and affiliates
- **Acknowledgment:** Thank you to Meta for React.

#### Electron
- **Website:** https://www.electronjs.org/
- **License:** MIT License
- **Copyright:** Copyright (c) Electron contributors
- **Acknowledgment:** Thank you to the Electron team.

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
MIT License

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
BSD 3-Clause License

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
Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

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
GNU GENERAL PUBLIC LICENSE
Version 2, June 1991

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
GNU AFFERO GENERAL PUBLIC LICENSE
Version 3, 19 November 2007

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

### Llama 3 Community License Agreement
```
Llama 3 Community License Agreement

Meta Platforms, Inc. ("Meta") grants you a non-exclusive, worldwide,
non-transferable and royalty-free limited license under Meta's intellectual
property rights to use, reproduce, distribute, copy, create derivative works
of, and make modifications to the Llama materials.

Full license: https://llama.meta.com/llama3/license/
```

---

## Special Thanks

We extend our heartfelt gratitude to:

### AI/ML Community
1. **IBM Research & IBM Granite Team** - For developing enterprise-grade open
   language models that power VA21's intelligent capabilities.

2. **Microsoft Research** - For ONNX Runtime, FARA technology, and Phi models
   that enable efficient, cross-platform AI inference and intelligent UI automation.

3. **Meta AI** - For LLaMA models and PyTorch framework.

4. **Hugging Face** - For democratizing AI and hosting the models we use.

5. **Ollama Team** - For making local LLM deployment accessible.

6. **ONNX Community** - For the open model exchange format.

### Open Source Community
7. **Debian Project** - For the most stable and versatile Linux distribution.

8. **Linux Foundation** - For stewardship of the Linux kernel.

9. **Flatpak & Flathub** - For revolutionizing Linux app distribution.

10. **The Open Source Community** - For building the foundation that makes
    projects like VA21 possible.

### Security & Privacy
11. **Security Researchers** - For their tireless work keeping systems safe.

12. **Privacy Advocates** - For championing user privacy and data protection.

### Inspiration
13. **The Zork/Infocom Legacy** - For showing that interfaces can be both
    functional and imaginative.

14. **All Contributors** - Every person who has contributed code, documentation,
    bug reports, or ideas.

---

## Model Attribution

When using VA21's AI features, please note the following model attributions:

| Feature | Primary Model | Provider | License |
|---------|--------------|----------|---------|
| Security Analysis | Guardian AI (ONNX) | VA21/Microsoft ONNX | MIT |
| Chat/Reasoning | Granite 4.0 | IBM | Apache 2.0 |
| Code Assistance | Granite 4.0 / Code Llama | IBM/Meta | Apache 2.0 / Llama License |
| UI Automation | FARA-inspired Agent | Microsoft | MIT |
| Local Fallback | Phi-3 / Ollama | Microsoft/Ollama | MIT |

---

## Contact

For licensing inquiries, please contact the VA21 development team.

---

*Last Updated: December 2024*
*VA21 Research OS v1.0.0-alpha.1 (Vinayaka)*

*Om Vinayaka - With gratitude to all who contribute to open innovation.* 🙏
