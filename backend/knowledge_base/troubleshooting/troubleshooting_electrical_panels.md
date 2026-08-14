# Electrical Panel Troubleshooting Guide

## 1. Circuit Breaker Keeps Tripping

### 1.1 Overload Trip

**Symptoms:** Main or branch breaker trips under load, can be reset but trips again when load is applied.

**Diagnosis Steps:**
1. Identify which breaker is tripping — main incomer or a specific branch circuit
2. Measure current draw on the circuit with a clamp meter
3. Compare measured current with the breaker rating

**Resolution:**
- If current exceeds breaker rating: redistribute loads across circuits or upgrade the breaker and cabling to handle the load
- If current is within rating but breaker still trips: the breaker may be worn — replace with a same-rated breaker
- For motor circuits: ensure breaker type is "D-curve" (motor-rated) not "B-curve" (lighting-rated), as motors draw 6-8x starting current

---

### 1.2 Earth Fault / RCD Trip

**Symptoms:** Residual Current Device (RCD/ELCB) trips, cannot be reset, or trips intermittently.

**Diagnosis Steps:**
1. Disconnect all circuits downstream of the RCD
2. Reset the RCD — if it holds, reconnect circuits one at a time to find the fault
3. Check for water ingress in outdoor junction boxes or socket outlets
4. Inspect appliance cables for damaged insulation

**Resolution:**
- Repair or replace the circuit with damaged insulation
- Dry out wet junction boxes and install IP-rated enclosures
- If no specific fault is found: the RCD may be overly sensitive (especially 30mA RCDs on long circuits) — consider a time-delayed RCD or splitting the circuit
- Replace faulty RCD if it trips with no load connected

---

## 2. Bus Bar Overheating

**Symptoms:** Discoloration on bus bars, burning smell from panel, elevated temperature readings on thermal scan, plastic components near bus bars showing deformation.

**Diagnosis Steps:**
1. Perform infrared thermography scan of all bus bar connections
2. Check torque on all bus bar bolts (refer to manufacturer spec — typically 20-25 Nm for copper bus bars)
3. Look for signs of arcing (pitting, carbon deposits) at connection points

**Resolution:**
- Re-torque all bus bar connections to manufacturer specifications
- Clean contact surfaces and apply anti-oxidant compound
- Replace bus bars with pitting or heat damage
- Ensure current loading does not exceed bus bar rating

**Warning:** Bus bar work must be performed by a qualified electrician with the panel de-energized. Overheating bus bars can cause fires.

---

## 3. ATS (Automatic Transfer Switch) Problems

### 3.1 ATS Does Not Switch to Generator

**Symptoms:** Mains power fails but the ATS does not start the generator or transfer to generator supply.

**Diagnosis Steps:**
1. Check the mains sensing relay — does the ATS detect that mains has failed?
2. Check generator start signal from ATS to generator control panel
3. Verify the generator starts independently when manually started
4. Check ATS timer settings — there is usually a 5-15 second delay before transfer

**Resolution:**
- If ATS does not sense mains failure: replace the voltage sensing relay or adjust voltage thresholds
- If ATS senses failure but does not send start signal: check the control wiring between ATS and generator
- If generator starts but ATS does not transfer: check the motorized changeover switch mechanism — may be mechanically stuck
- Reset ATS controller and verify timer settings

---

### 3.2 ATS Keeps Switching Back and Forth

**Symptoms:** ATS rapidly switches between mains and generator (chattering), causing power interruptions.

**Diagnosis Steps:**
1. Measure mains voltage — may be fluctuating near the ATS threshold
2. Check ATS hysteresis settings (voltage window between "fail" and "restore")
3. Check the time delay settings for re-transfer to mains

**Resolution:**
- Increase the ATS hysteresis window (e.g., fail at 180V, restore at 200V instead of fail at 190V, restore at 195V)
- Increase the re-transfer timer to 60-120 seconds to avoid rapid switching
- If mains is consistently unstable: install a voltage stabilizer before the ATS

---

## 4. Power Factor Correction Panel Issues

### 4.1 Capacitor Bank Not Switching

**Symptoms:** Power factor remains low despite PFC panel being energized, capacitor contactors not engaging.

**Resolution:**
- Check the PFC controller — it may need recalibration with a CT (current transformer) reading
- Inspect contactors for welded contacts or coil failure
- Check capacitor health with a capacitance meter — replace blown capacitors
- Verify CT is correctly installed on the correct phase

---

## 5. Panel Communication Failures

### 5.1 Remote Monitoring Not Working

**Symptoms:** SCADA or remote monitoring system cannot communicate with panel meters/relays.

**Diagnosis Steps:**
1. Check communication cables (RS485/Modbus or Ethernet)
2. Verify device addresses are correctly configured (no duplicate addresses)
3. Check baud rate and protocol settings match between master and slave devices
4. Test with a laptop connected directly to the device

**Resolution:**
- Replace damaged communication cables
- Reconfigure device addresses to eliminate conflicts
- Match communication parameters (baud rate, parity, stop bits)
- Update firmware on panel meters if available

---

## When to Call Mikano Electrical Service

Contact Mikano's electrical panel team if:
- Bus bar overheating is detected (fire risk)
- ATS mechanical changeover mechanism is stuck
- Panel requires load balancing or circuit redesign
- Type-testing certification is needed for new installations
- Warranty service is required on Mikano-manufactured panels

**Service Line:** 07001234567
**Email:** panels@mikano-intl.com
