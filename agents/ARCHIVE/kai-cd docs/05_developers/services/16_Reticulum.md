---
title: "Reticulum"
description: "Technical specification for reticulum"
type: "service"
status: "current"
priority: "medium"
last_updated: "2025-06-22"
agent_notes: "AI agent guidance for implementing reticulum"
---

# Reticulum Network Service Documentation

This document provides a detailed overview of the integration between Kai-CD and Reticulum Network. Reticulum is a cryptography-based networking stack for building decentralized, resilient mesh networks that can operate even in adverse conditions with very high latency and extremely low bandwidth.

- **Official Website:** [https://reticulum.network/](https://reticulum.network/)
- **GitHub Repository:** [https://github.com/markqvist/reticulum](https://github.com/markqvist/reticulum)
- **Documentation:** [https://markqvist.github.io/Reticulum/manual/](https://markqvist.github.io/Reticulum/manual/)
- **Sideband GUI:** [https://unsigned.io/website/sideband/](https://unsigned.io/website/sideband/)
- **MeshChat GUI:** [https://github.com/liamcottle/reticulum-meshchat](https://github.com/liamcottle/reticulum-meshchat)

## Overview

Reticulum enables the construction of both small and potentially planetary-scale networks without any need for hierarchical or bureaucratic structures to control or manage them, while ensuring individuals and communities full sovereignty over their own network segments.

### Notable Characteristics

- **No Source Addresses:** Packets transmitted include no information about their origin
- **Decentralized Address Space:** Anyone can allocate addresses as needed
- **End-to-End Connectivity:** New addresses become globally reachable in seconds to minutes
- **Self-Sovereign Addresses:** Addresses are portable and can be moved physically
- **Encrypted by Default:** All communication uses strong, modern encryption
- **Forward Secrecy:** Ephemeral keys and forward secrecy by default
- **No Unencrypted Links:** It's impossible to establish unencrypted connections

## Capabilities & Endpoints

### 1. Mesh Networking (`MeshNetworkingCapability`)

#### Get Network Nodes
- **Endpoint:** `GET /nodes`
- **Description:** Retrieves information about known nodes in the Reticulum network
- **Response:** List of active nodes with their destinations and status

#### Send Message
- **Endpoint:** `POST /message`
- **Description:** Send a message to a specific destination on the network
- **Parameters:**
  - `destination`: Target destination hash
  - `message`: Message content (automatically encrypted)
  - `priority`: Message priority level

#### Get Messages
- **Endpoint:** `GET /messages`
- **Description:** Retrieve messages received by this node
- **Response:** List of received messages with metadata

#### Announce Destination
- **Endpoint:** `POST /announce`
- **Description:** Announce this node's destination to the network
- **Parameters:**
  - `destination_name`: Human-readable name for the destination
  - `app_data`: Optional application-specific data

#### Get Destinations
- **Endpoint:** `GET /destinations`
- **Description:** Get list of known destinations on the network
- **Response:** Known destinations with their paths and status

### 2. Health (`HealthCapability`)

- **Endpoint:** `GET /status`
- **Description:** Check if the Reticulum daemon is running and network interfaces are active

## Network Interface Configuration

Reticulum supports multiple interface types for different networking scenarios:

### TCP/IP Interface
For connecting to other nodes over the internet or local networks:
- **Target Host:** Remote Reticulum node address
- **Target Port:** TCP port (default: 4965 for testnet)
- **Use Case:** Connecting to the public testnet or remote nodes

### I2P Network Interface  
For anonymous networking over the I2P network:
- **I2P Peer:** I2P destination address (.b32.i2p address)
- **Use Case:** Anonymous, censorship-resistant communication

### LoRa Radio Interface
For long-range radio communication:
- **Frequency:** Operating frequency in MHz (e.g., 915.0 for US)
- **Bandwidth:** Signal bandwidth (7.8 kHz to 500 kHz)
- **Spreading Factor:** Error correction level (7-12)
- **Coding Rate:** Forward error correction (4/5 to 4/8)
- **TX Power:** Transmission power in dBm (5-20)
- **Use Case:** Long-range, low-power mesh networking

### Packet Radio Interface
For traditional packet radio systems:
- **Frequency:** Operating frequency
- **TX Power:** Transmission power
- **Use Case:** Integration with existing packet radio networks

### Serial Interface
For direct serial connections:
- **Device:** Serial device path (e.g., /dev/ttyUSB0)
- **Baud Rate:** Serial communication speed
- **Use Case:** Direct point-to-point connections

### KISS Protocol Interface
For Terminal Node Controller (TNC) connections:
- **Device:** KISS TNC device
- **Use Case:** Integration with amateur radio equipment

## Authentication & Security

Reticulum uses **cryptographic identities** instead of traditional authentication:

- **Identity Generation:** Each node generates a unique cryptographic identity
- **No Passwords:** Authentication is based on public key cryptography
- **Perfect Forward Secrecy:** Keys are ephemeral and rotated regularly
- **End-to-End Encryption:** All communication is encrypted by default

## Installation & Setup

### 1. Install Reticulum
```bash
pip install rns
```

### 2. Initialize Configuration
```bash
rnsd --config
```

### 3. Configure Interfaces
Edit `~/.reticulum/config` to add network interfaces:

```ini
# TCP Interface to Testnet
[[RNS Testnet Amsterdam]]
  type = TCPClientInterface
  enabled = yes
  target_host = amsterdam.connect.reticulum.network
  target_port = 4965

# I2P Interface  
[[RNS Testnet I2P Hub]]
  type = I2PInterface
  enabled = yes
  peers = g3br23bvx3lq5uddcsjii74xgmn6y5q325ovrkq2zw2wbzbqgbuq.b32.i2p
```

### 4. Start Reticulum Daemon
```bash
rnsd
```

## GUI Applications

### Sideband
- **Website:** [https://unsigned.io/website/sideband/](https://unsigned.io/website/sideband/)
- **Description:** Official GUI application for Reticulum with messaging, file transfer, and network management
- **Platforms:** iOS, Android, macOS, Linux, Windows

### MeshChat
- **Repository:** [https://github.com/liamcottle/reticulum-meshchat](https://github.com/liamcottle/reticulum-meshchat)
- **Description:** Web-based chat interface for Reticulum networks
- **Features:** Real-time messaging, file sharing, network visualization

## Use Cases

### Emergency Communications
- Disaster response scenarios where traditional infrastructure is unavailable
- Remote area communications with minimal infrastructure
- Backup communication systems for critical applications

### Privacy-Focused Networking
- Anonymous communication over I2P
- Censorship-resistant messaging
- Sovereign community networks

### IoT & Sensor Networks
- Low-power, long-range sensor networks using LoRa
- Mesh networks for remote monitoring
- Agricultural and environmental monitoring systems

### Amateur Radio Integration
- Modern packet radio systems
- Digital modes for amateur radio
- Emergency communication networks

## Testnet Access

Join the public testnet to experiment with Reticulum:

### Amsterdam Hub (TCP)
- **Host:** amsterdam.connect.reticulum.network
- **Port:** 4965

### BetweenTheBorders Hub (TCP)
- **Host:** reticulum.betweentheborders.com  
- **Port:** 4242

### I2P Testnet Hub
- **Address:** g3br23bvx3lq5uddcsjii74xgmn6y5q325ovrkq2zw2wbzbqgbuq.b32.i2p

## Security Considerations

- **Experimental Software:** Reticulum is relatively young and should be considered experimental
- **Radio Licensing:** Radio interfaces may require appropriate amateur radio licenses
- **Hardware Requirements:** LoRa and radio interfaces require compatible hardware
- **Testnet Stability:** The testnet may contain experimental features and unstable behavior

## Development Resources

- **Manual:** [https://markqvist.github.io/Reticulum/manual/](https://markqvist.github.io/Reticulum/manual/)
- **Examples:** Available in the Reticulum repository under `/Examples`
- **API Documentation:** Included with the Reticulum installation
