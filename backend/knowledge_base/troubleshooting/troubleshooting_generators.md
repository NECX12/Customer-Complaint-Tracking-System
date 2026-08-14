# Generator Troubleshooting Guide

## 1. Generator Will Not Start

### 1.1 Battery Issues (Most Common)

**Symptoms:** Clicking sound when pressing start, no crank, slow cranking, dashboard shows low voltage.

**Diagnosis Steps:**
1. Check battery voltage with a multimeter — should read at least 12.4V (24V systems: 24.8V)
2. Inspect battery terminals for corrosion (white/green buildup)
3. Check cable connections for looseness
4. Look for swollen or leaking battery (replace immediately if found)

**Resolution:**
- Clean corroded terminals with a wire brush and apply anti-corrosion grease
- Tighten loose connections to manufacturer torque spec
- Charge battery with a smart charger if voltage is below 12.4V
- Replace battery if it cannot hold charge or is older than 3 years
- For standby generators: install a battery maintainer/trickle charger

**Prevention:** Run the generator for at least 15 minutes every two weeks to keep the battery charged. Schedule battery replacement every 2-3 years as preventive maintenance.

---

### 1.2 Fuel System Problems

**Symptoms:** Engine cranks but does not fire, engine starts then stalls, fuel warning light on dashboard.

**Diagnosis Steps:**
1. Check fuel level — gauge may be faulty, so visually inspect the tank
2. Check fuel age — diesel degrades after 6-12 months of storage
3. Inspect fuel filter for blockage (dark/cloudy fuel visible through clear filter housing)
4. Check for air locks in the fuel line (common after filter replacement or running dry)
5. Inspect fuel lines for cracks, leaks, or kinks

**Resolution:**
- Refill with fresh, clean diesel if tank is low or fuel is stale
- Replace fuel filter if clogged (use genuine Mikano/Perkins/MTU filter)
- Bleed the fuel system to remove air locks: loosen the bleed screw on the fuel injection pump, operate the hand primer until fuel flows without bubbles, then retighten
- Drain and clean the fuel tank if water contamination is suspected (water settles at the bottom)

**Prevention:** Use fuel stabilizer for generators that run infrequently. Schedule fuel filter replacement every 250-500 hours. Never let the tank run below 25% to avoid sediment intake.

---

### 1.3 Low Oil Level or Wrong Oil Viscosity

**Symptoms:** "Low Oil Pressure" alarm, engine refuses to crank, engine shuts down shortly after starting.

**Diagnosis Steps:**
1. Check oil level using the dipstick — should be between MIN and MAX marks
2. Check oil color — should be amber/brown, not black and gritty
3. Verify correct oil grade per the operation manual (typically 15W-40 for diesel generators)

**Resolution:**
- Top up oil to the correct level with the specified grade
- If oil is black/degraded, perform a full oil change with filter replacement
- Check for oil leaks under the generator and around gaskets

**Prevention:** Check oil level weekly. Change oil and filter every 250 hours or 6 months.

---

## 2. Generator Starts but Shuts Down Unexpectedly

### 2.1 Overload / Overcurrent

**Symptoms:** Generator runs for a few minutes then trips, "Overload" alarm on control panel, lights dim before shutdown.

**Diagnosis Steps:**
1. Calculate total connected load (sum of all appliances in watts/kVA)
2. Compare with generator rated capacity — load should not exceed 80% of rated output
3. Check for motor-driven appliances (AC units, pumps) that draw high starting current

**Resolution:**
- Reduce connected load to below 80% of rated capacity
- Stagger the startup of heavy appliances (start AC units one at a time with 30-second intervals)
- For recurring issues: consider upgrading to a higher-capacity generator
- Install a load management system for automatic load shedding

**Prevention:** Never connect a total load exceeding 75-80% of generator rating. Use a power meter to monitor real-time load.

---

### 2.2 Overheating

**Symptoms:** "High Temperature" alarm, coolant temperature gauge in red zone, steam or coolant leak visible, generator shuts down after 15-30 minutes.

**Diagnosis Steps:**
1. Check coolant level in the radiator (when engine is cool)
2. Inspect radiator fins for dirt, debris, or blockage
3. Check if the cooling fan is operating
4. Inspect the thermostat for failure (stuck closed = no coolant flow)
5. Verify the generator is installed with adequate ventilation clearance (minimum 1.5m on all sides)

**Resolution:**
- Top up coolant with the correct antifreeze/water mix (typically 50/50)
- Clean radiator fins with compressed air or a soft brush
- Replace thermostat if stuck
- Ensure exhaust system is clear and not recirculating hot air
- For enclosed installations: verify ventilation fans are working

**Prevention:** Check coolant level weekly. Clean radiator monthly in dusty environments. Flush and replace coolant annually.

---

### 2.3 Speed/Frequency Errors

**Symptoms:** "Over Speed" or "Under Speed" alarm, engine sound fluctuates (surging/hunting), output frequency unstable (should be 50Hz).

**Diagnosis Steps:**
1. Check fuel supply and filter condition (restricted fuel = under speed)
2. Inspect the electronic governor/actuator
3. Check the speed sensor (magnetic pickup) for damage or misalignment
4. Verify no sudden load changes are causing speed fluctuation

**Resolution:**
- Replace clogged fuel filter
- Adjust governor settings (requires trained technician with diagnostic software)
- Clean or replace the speed sensor
- For persistent hunting: may need governor recalibration or actuator replacement

**Prevention:** Regular fuel filter changes. Annual governor system inspection.

---

## 3. Engine Runs but No Power Output

### 3.1 AVR (Automatic Voltage Regulator) Failure

**Symptoms:** Engine runs normally, voltmeter shows 0V or very low voltage, all connected equipment is dead.

**Diagnosis Steps:**
1. Check the voltmeter/output display on the control panel
2. Test output terminals with a multimeter
3. Inspect the AVR unit for burn marks or damaged components
4. Check the excitation circuit wiring

**Resolution:**
- Replace the AVR with a genuine Mikano replacement part
- Check and repair any damaged wiring in the excitation circuit
- After AVR replacement, the generator may need to be "flashed" (residual magnetism restored)

**Warning:** AVR replacement should be performed by a qualified technician. Incorrect installation can damage the alternator.

---

### 3.2 Circuit Breaker Tripped

**Symptoms:** Engine runs, partial or no power output, circuit breaker in the OFF position.

**Resolution:**
- Disconnect all loads
- Reset the circuit breaker
- Reconnect loads gradually
- If breaker trips again immediately: suspect a short circuit in the output wiring or connected equipment

---

## 4. Excessive Noise or Vibration

### 4.1 Noise Exceeds Acceptable Levels

**Symptoms:** Neighbors complaining, noise measurements above 85 dB at property boundary, vibration felt in adjacent buildings.

**Diagnosis Steps:**
1. Measure noise level at 7 meters from the generator (standard test distance)
2. Check if the acoustic canopy/enclosure is intact (panels secure, seals not degraded)
3. Inspect exhaust silencer for damage or blockage
4. Check anti-vibration mounts for wear

**Resolution:**
- Install or replace the acoustic enclosure (Mikano Model AE-100 for ≤30kVA, AE-200 for ≤100kVA, AE-500 for ≤500kVA)
- Replace exhaust silencer (residential grade: ≤65 dB, hospital grade: ≤55 dB)
- Replace worn anti-vibration mounts
- For extreme cases: build a dedicated generator room with acoustic treatment

**Compliance:** Lagos State EPA noise limit for residential areas is 75 dB during the day (7am-10pm) and 65 dB at night.

---

## 5. Excessive Smoke

### 5.1 Black Smoke

**Cause:** Incomplete combustion — too much fuel, not enough air.
**Check:** Air filter (clogged), injectors (worn/blocked), turbocharger (if equipped), overloading.

### 5.2 White Smoke

**Cause:** Water in combustion chamber or unburned fuel.
**Check:** Head gasket (blown), coolant leak into cylinders, incorrect injection timing, very cold startup (normal for first few minutes).

### 5.3 Blue Smoke

**Cause:** Oil burning in the combustion chamber.
**Check:** Worn piston rings, valve stem seals, overfilled oil, turbocharger oil seal.

---

## 6. Fuel Leaks

**Symptoms:** Diesel smell, visible fuel puddle under generator, fuel consumption higher than normal.

**Diagnosis Steps:**
1. Inspect fuel tank for cracks or corrosion
2. Check fuel line connections and hose condition
3. Inspect fuel filter housing seals
4. Check injector return lines

**Resolution:**
- Replace damaged fuel lines or hoses
- Tighten loose fittings
- Replace fuel filter housing seals
- For tank damage: professional repair or tank replacement

**Warning:** Fuel leaks are a fire hazard. Shut down the generator immediately if a fuel leak is detected during operation.

---

## When to Call Mikano Service

Contact Mikano's authorized service team if:
- Basic checks (battery, fuel, oil) do not resolve the issue
- Control panel shows persistent fault codes after reset
- You see evidence of internal engine damage (metal in oil, knocking sounds)
- The generator requires governor recalibration or AVR replacement
- Any work involving the fuel injection system, turbocharger, or alternator windings

**Emergency Service Line:** 07001234567
**Service Portal:** service.mikano-intl.com
