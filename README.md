# check_varnish.py

A monitoring plugin for [Varnish Cache](https://varnish-cache.org/) that reports cache metrics and supports Nagios-style threshold alerts.

Originally by Olivier Hanesse, maintained by Claudio Kuenzler.

## 📦 Features

- Check any Varnish stat field (via `varnishstat`)
- Supports Varnish >= 4.x, including >= 6.5.0 JSON counters
- Works with custom instance names (`-n`)
- Cache hit ratio calculation (`-r`)
- Exit codes compatible with Nagios/Icinga
- No dependencies beyond `Python 3` and Varnish CLI tools

---

## ✅ Requirements

- Python
- `varnishstat` and `varnishadm` in `/usr/bin` or accessible in `$PATH`
- Varnish running and configured with shared memory logging
- User must have permission to read `/etc/varnish/secret` and access the Varnish instance

---

## 📥 Installation

```bash
wget https://raw.githubusercontent.com/olivierHa/check_varnish/master/check_varnish.py
chmod +x check_varnish.py
```

Ensure the shebang uses Python:

```bash
#!/usr/bin/env python
```

If you are facing this issue:
```
/usr/bin/env: 'python': No such file or directory
```

Then you need tochange ```#!/usr/bin/env python``` to ```#!/usr/bin/env python3``` in check_varnish.py.

---

## 🔧 Usage

```bash
./check_varnish.py -f FIELD[,FIELD...] [OPTIONS]
```

### Options

| Flag           | Description                                                    |
|----------------|----------------------------------------------------------------|
| `-f`, `--field`  | Varnishstat field(s) to monitor (required)                   |
| `-n`, `--name`   | Instance name (directory inside /var/lib/varnish)            |
| `-r`, `--hitratio` | Enable cache hit ratio calculation                         |
| `-w`, `--warning`  | Warning threshold (for single field)                       |
| `-c`, `--critical` | Critical threshold (for single field)                      |

---

## 🔍 Examples

### Cache hit ratio (2 fields)

```bash
./check_varnish.py -f MAIN.cache_hit,MAIN.cache_miss -r
```

**Output:**

```
VARNISH OK - MAIN.cache_hit is 22783 - MAIN.cache_miss is 19381 - Cache Hit Rate is 0.54 | MAIN.cache_hit=22783;0;0;; MAIN.cache_miss=19381;0;0;; hitrate=0.54;0;0;;
```

---

### Single metric with thresholds

```bash
./check_varnish.py -f MAIN.sess_dropped -w 5 -c 10
```

**Output:**

```
VARNISH OK - MAIN.sess_dropped is 0 | MAIN.sess_dropped=0;5;10;;
```

---

### Using a named instance

If Varnish uses a non-default workdir (check /var/lib/varnish), use:

```bash
./check_varnish.py -f MAIN.cache_hit,MAIN.cache_miss -r -n vps129645.whmpanels.com
```

---

## ⚠️ Troubleshooting

**❌ Could not get hold of varnishd, is it running?**

Possible causes:
- Wrong instance name: use -n with the correct directory under /var/lib/varnish
- Insufficient permissions to read /etc/varnish/secret
- Script run as non-root without access to shared memory

**Fix by:**

```bash
sudo usermod -aG varnish your_user
sudo chmod 640 /etc/varnish/secret
sudo chgrp varnish /etc/varnish/secret
```

Then restart your shell session or run:

```bash
su - your_user
```

---

## 📋 Exit Codes

| Code | Meaning           |
|------|-------------------|
| 0    | OK                |
| 1    | WARNING           |
| 2    | CRITICAL          |
| 3    | UNKNOWN/ERROR     |

---

## 📚 Getting Available Fields

```bash
varnishstat -l         # list all fields
varnishstat -j | jq .  # parseable output
```

---

## 📝 License

GPLv2 or later — see original script for details.

---

## 🔗 Sources

- https://github.com/olivierHa/check_varnish
- https://www.claudiokuenzler.com
