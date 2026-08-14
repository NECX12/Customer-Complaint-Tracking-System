# Inverter Troubleshooting Guide

## 1. Inverter Shows No Output / Will Not Power On

### 1.1 Battery Completely Discharged

**Symptoms:** Inverter panel is blank/dark, no indicator lights, no beeping.

**Diagnosis Steps:**
1. Check battery voltage — should be above 10.5V per 12V battery (21V for 24V systems)
2. Check battery terminal connections for looseness or corrosion
3. Verify the DC breaker/fuse between battery and inverter is not tripped

**Resolution:**
- If voltage is below 10.5V: batteries are deeply discharged. Connect to mains power and allow 6-8 hours of charging before attempting to use
- Clean corroded terminals with baking soda solution and wire brush
- Replace blown DC fuse with correct rating (check inverter manual for fuse specification)
- If batteries are older than 3 years and will not hold charge: replace battery bank

**Prevention:** Avoid running batteries below 40% charge (most inverters auto-shutdown at 20%). Check battery water levels monthly for tubular lead-acid batteries.

---

## 2. Inverter Powers On but No Output to Loads

### 2.1 Output Overload Protection Triggered

**Symptoms:** Inverter display shows "OVERLOAD" or overload LED is red, beeping alarm, connected appliances do not work.

**Diagnosis Steps:**
1. Check total connected load versus inverter rated capacity
2. Look for motor-driven appliances that may have high starting current (fridges, AC, pumps)
3. Check if any connected appliance has a short circuit

**Resolution:**
- Disconnect all loads, then reconnect one at a time to identify the overloading device
- For motor loads: use a soft-start device or ensure the inverter rating is at least 3x the motor's running wattage
- If a single appliance trips the inverter: that appliance may have an internal fault
- Reset overload by turning the inverter off, waiting 30 seconds, then turning back on

---

### 2.2 Internal Transfer Switch Failure

**Symptoms:** Inverter display shows normal readings, but outlets have no power. Mains power also does not pass through.

**Resolution:**
- This indicates a relay or transfer switch failure inside the inverter
- Power off the inverter and contact Mikano service — internal relay replacement required
- **Do not attempt to bypass the transfer switch** — this is a safety hazard

---

## 3. Power Fluctuations from Inverter

### 3.1 Output Voltage Instability

**Symptoms:** Lights connected to inverter flicker, sensitive electronics malfunction, voltage display on inverter fluctuates between 180V-260V.

**Diagnosis Steps:**
1. Measure output voltage at the inverter terminals with a multimeter
2. Check if fluctuation occurs on battery power only or also on mains bypass
3. Check battery voltage — low battery causes voltage sag
4. Measure the mains input voltage — if input is unstable (common in Nigeria), the inverter may be passing through unstable power

**Resolution:**
- **If on battery power:** Check battery health (load test). Weak batteries cause output voltage instability. Replace if batteries are aged or degraded.
- **If on mains bypass:** The issue is with the utility supply, not the inverter. Install a voltage stabilizer before the inverter input.
- **If both:** The inverter's internal voltage regulation circuit may be faulty — contact Mikano service.

**Common Cause in Nigeria:** Unstable PHCN/DisCo utility supply (voltages ranging 140V-280V) can cause the inverter's charging circuit to malfunction over time. A dedicated voltage stabilizer on the input is recommended.

---

### 3.2 Inverter Making Buzzing/Humming Noise During Operation

**Symptoms:** Audible buzzing from the inverter unit, especially under load.

**Diagnosis Steps:**
1. Light buzzing under heavy load is normal for transformer-based inverters
2. Loud buzzing or rattling is abnormal

**Resolution:**
- If buzzing occurs only on mains bypass: the internal transformer may have loose laminations — requires service
- If buzzing occurs on battery mode under heavy load: reduce connected load to below 80% of rated capacity
- Persistent loud buzzing: contact Mikano service for internal inspection

---

## 4. Battery Not Charging from Mains

### 4.1 Charging Circuit Issue

**Symptoms:** Inverter is connected to mains, "Charging" indicator does not light up, battery voltage does not increase over time.

**Diagnosis Steps:**
1. Verify mains power is actually reaching the inverter (check input voltage display)
2. Check if input voltage is within acceptable range (typically 160V-280V for Nigerian inverters)
3. Inspect the charging fuse (located inside or on the back panel)
4. Check battery connections — a loose connection prevents charging

**Resolution:**
- If input voltage is too low (<160V): install a voltage stabilizer before the inverter
- Replace blown charging fuse with correct rating
- Tighten all battery connections
- If the above does not resolve: the internal charging board may be faulty — contact Mikano service

---

### 4.2 Battery Charges but Drains Too Quickly

**Symptoms:** Batteries reach full charge but deplete within 1-2 hours under normal load.

**Diagnosis Steps:**
1. Calculate expected backup time: Battery Ah × Battery Voltage ÷ Load Watts × 0.8 (efficiency factor)
   - Example: 200Ah × 24V ÷ 1000W × 0.8 = ~3.8 hours
2. If actual time is significantly less: batteries are degraded
3. Check individual battery voltages — all batteries in a bank should be within 0.1V of each other

**Resolution:**
- If batteries are older than 2-3 years (lead-acid) or 5 years (lithium): replace the battery bank
- If one battery is significantly lower voltage than others: that battery is dead — replace the entire bank (mixing old and new batteries causes premature failure)
- Check for phantom loads — appliances drawing power even when turned off (TV standby, phone chargers)

---

## 5. Inverter Display Shows Error Codes

### Common Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| E01 | Output short circuit | Disconnect all loads, check wiring for shorts, reset |
| E02 | Overload | Reduce connected load below 80% of rated capacity |
| E03 | Battery low voltage | Recharge batteries; replace if they cannot hold charge |
| E04 | Battery over voltage | Check charger settings; may indicate charger malfunction |
| E05 | Over temperature | Ensure ventilation is clear; clean dust from vents; check fan |
| E06 | Internal fan failure | Fan replacement required — contact Mikano service |
| E07 | Charging fault | Check mains input, charging fuse, battery connections |

---

## 6. Inverter and Solar Panel Integration Issues

### 6.1 Solar Panels Not Charging Batteries

**Symptoms:** Solar charge controller shows low or zero input, batteries not charging during daylight.

**Diagnosis Steps:**
1. Check solar panel voltage at the charge controller input (should match panel specifications)
2. Inspect panel surface for dirt, shade, or damage
3. Verify wiring connections between panels and charge controller
4. Check charge controller settings — battery type must match (lead-acid vs lithium)

**Resolution:**
- Clean solar panels with water and soft cloth
- Remove shading obstructions (tree branches, new construction)
- Repair or replace damaged wiring
- Reconfigure charge controller for correct battery type

---

## When to Call Mikano Service

Contact Mikano's inverter service team if:
- Error codes persist after troubleshooting
- Internal components (relay, transformer, charging board) are suspected faulty
- Battery bank replacement is needed (for proper sizing and installation)
- Solar integration configuration is required
- Warranty claim is applicable (within 12 months of purchase, with proof of purchase)

**Service Line:** 07001234567
**Email:** inverter.support@mikano-intl.com
