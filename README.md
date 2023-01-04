# Activist short-selling bot
**DISCLAIMER**:  This is a purely research project that does not aim to provide any investment advice.
This repo contains a custom app for automated CFD trading based on twitter signals. The main idea is to monitor the twitter accounts of selected activist investment funds who are known for exposing poorly-managed or fraudulent publicly traded companies, and use their reports as short-selling signals. This app consists of two main parts: a twitter client responsible for real-time monitoring and signal extraction and a broker client responsible for automatically opening and managing a leveraged short CFD position. One example of such an opportunity is the famous Nikola Corp whose share price saw a whopping 76% decline in a month following a company analysis report issued by Hindenburg Research, an investigative activist fund. After interleaving the twitter post history of major activist funds with their targets' share prices, we found an unstable yet potentially huge market opportunity.

**Components**:
- `utils_twitter` contains scripts for streamed monitoring of selected twitter accounts for trade signal.
- `utils_platform` contains a custom wrapper client built on top of trading REST API provided by [IG](www.ig.com), a CFD-trading broker.

**Basic workflow**:
1. Monitor tweet stream until trading signal is received.
2. Extract target ticker from the signal.
3. Open a short leveraged CFD position on the extracted ticker. The size and parameters of the position are determined by user-defined rules.
4. Hold and monitor the position until trailing stop level or trailing stop loss is hit.
5. Close the position.

The main entity of this project is the `MKTClient` class in `utils_platform/mclient.py`.
Apart from the app components, the commited code is intentionally incomplete.