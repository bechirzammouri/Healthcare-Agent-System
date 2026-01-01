# SyntheticMass Healthcare Data: Relationships & Schema Guide

## 📊 Overview
This document describes the relationships between different healthcare datasets in the SyntheticMass sampled data. All datasets are interconnected through patient encounters and medical events.

---

## 🗂️ Dataset Summary

| Dataset | Records | Description |
|---------|---------|-------------|
| **Patients** | 23 | Core demographic information |
| **Encounters** | 83 | Healthcare visits/interactions |
| **Observations** | 486 | Clinical measurements & findings |
| **Careplans** | 127 | Treatment plans & interventions |
| **Conditions** | 70 | Diagnoses & health conditions |
| **Medications** | 78 | Prescribed drugs |
| **Procedures** | 42 | Medical procedures performed |
| **Immunizations** | 40 | Vaccines administered |

---

## 📋 Detailed Dataset Schemas

### 1. **PATIENTS** (Core Entity)
**Purpose:** Central demographic and identity information

| Column | Description |
|--------|-------------|
| `ID` | 🔑 Primary Key - Unique patient identifier |
| `BIRTHDATE` | Date of birth |
| `DEATHDATE` | Date of death (if applicable) |
| `SSN` | Social Security Number |
| `PREFIX, FIRST, LAST, SUFFIX` | Name components |
| `MARITAL` | Marital status |
| `RACE` | Race |
| `ETHNICITY` | Ethnicity |
| `GENDER` | Gender |
| `BIRTHPLACE` | Place of birth |
| `ADDRESS` | Current address |

**Relationships:**
- **1 Patient → Many Encounters** (One patient can have multiple visits)

---

### 2. **ENCOUNTERS** (Central Hub)
**Purpose:** Healthcare visits or interactions

| Column | Description |
|--------|-------------|
| `ID` | 🔑 Primary Key - Unique encounter identifier |
| `DATE` | Date of encounter |
| `PATIENT` | 🔗 Foreign Key → PATIENTS.ID |
| `CODE` | Medical code for encounter type |
| `DESCRIPTION` | Type of visit (e.g., Outpatient, Emergency, Death Certification) |
| `REASONCODE` | Code for visit reason |
| `REASONDESCRIPTION` | Why patient came in |

**Relationships:**
- **Many Encounters → 1 Patient**
- **1 Encounter → Many Observations**
- **1 Encounter → Many Medications**
- **1 Encounter → Many Procedures**
- **1 Encounter → Many Careplans**
- **1 Encounter → Many Immunizations**
- **1 Encounter → Many Conditions** (diagnosed during visit)

---

### 3. **OBSERVATIONS**
**Purpose:** Clinical measurements, lab results, and diagnostic findings

| Column | Description |
|--------|-------------|
| `DATE` | Date of observation |
| `PATIENT` | 🔗 Foreign Key → PATIENTS.ID |
| `ENCOUNTER` | 🔗 Foreign Key → ENCOUNTERS.ID |
| `CODE` | Observation code (LOINC/SNOMED) |
| `DESCRIPTION` | What was observed/measured |
| `VALUE` | Measured value |
| `UNITS` | Unit of measurement |

**Examples:** Blood pressure, weight, lab results, vital signs

**Relationships:**
- **Many Observations → 1 Patient**
- **Many Observations → 1 Encounter**

---

### 4. **CONDITIONS**
**Purpose:** Diagnoses and ongoing health conditions

| Column | Description |
|--------|-------------|
| `START` | When condition began |
| `STOP` | When condition ended (blank if ongoing) |
| `PATIENT` | 🔗 Foreign Key → PATIENTS.ID |
| `ENCOUNTER` | 🔗 Foreign Key → ENCOUNTERS.ID (where diagnosed) |
| `CODE` | Condition code (ICD/SNOMED) |
| `DESCRIPTION` | Condition name |

**Examples:** Hypertension, Diabetes, Pulmonary emphysema

**Relationships:**
- **Many Conditions → 1 Patient**
- **Many Conditions → 1 Encounter** (initial diagnosis)
- **1 Condition → Many Medications** (treatment)

---

### 5. **MEDICATIONS**
**Purpose:** Prescribed drugs and treatments

| Column | Description |
|--------|-------------|
| `START` | When medication started |
| `STOP` | When medication stopped |
| `PATIENT` | 🔗 Foreign Key → PATIENTS.ID |
| `ENCOUNTER` | 🔗 Foreign Key → ENCOUNTERS.ID (where prescribed) |
| `CODE` | Medication code (RxNorm) |
| `DESCRIPTION` | Medication name and dosage |
| `REASONCODE` | 🔗 References CONDITIONS.CODE |
| `REASONDESCRIPTION` | Why medication was prescribed |

**Examples:** Penicillin, Advair, blood pressure medications

**Relationships:**
- **Many Medications → 1 Patient**
- **Many Medications → 1 Encounter**
- **Many Medications → 1 Condition** (reason for prescription)

---

### 6. **PROCEDURES**
**Purpose:** Medical procedures and interventions performed

| Column | Description |
|--------|-------------|
| `DATE` | When procedure was performed |
| `PATIENT` | 🔗 Foreign Key → PATIENTS.ID |
| `ENCOUNTER` | 🔗 Foreign Key → ENCOUNTERS.ID |
| `CODE` | Procedure code (CPT/SNOMED) |
| `DESCRIPTION` | Procedure name |
| `REASONCODE` | Why procedure was done |
| `REASONDESCRIPTION` | Reason description |

**Examples:** Colonoscopy, Documentation of medications, surgical procedures

**Relationships:**
- **Many Procedures → 1 Patient**
- **Many Procedures → 1 Encounter**

---

### 7. **CAREPLANS**
**Purpose:** Treatment plans and ongoing care management

| Column | Description |
|--------|-------------|
| `ID` | 🔑 Primary Key - Careplan identifier |
| `START` | When careplan started |
| `STOP` | When careplan ended |
| `PATIENT` | 🔗 Foreign Key → PATIENTS.ID |
| `ENCOUNTER` | 🔗 Foreign Key → ENCOUNTERS.ID (where initiated) |
| `CODE` | Careplan code |
| `DESCRIPTION` | Type of care/intervention |
| `REASONCODE` | 🔗 References CONDITIONS.CODE |
| `REASONDESCRIPTION` | Condition being managed |

**Examples:** COPD management plan, Exercise therapy, Diabetes self-management

**Relationships:**
- **Many Careplans → 1 Patient**
- **Many Careplans → 1 Encounter**
- **Many Careplans → 1 Condition** (target condition)

---

### 8. **IMMUNIZATIONS**
**Purpose:** Vaccines administered to patients

| Column | Description |
|--------|-------------|
| `DATE` | When vaccine was given |
| `PATIENT` | 🔗 Foreign Key → PATIENTS.ID |
| `ENCOUNTER` | 🔗 Foreign Key → ENCOUNTERS.ID |
| `CODE` | Vaccine code (CVX) |
| `DESCRIPTION` | Vaccine name |

**Examples:** Influenza vaccine, COVID-19, childhood immunizations

**Relationships:**
- **Many Immunizations → 1 Patient**
- **Many Immunizations → 1 Encounter**


## 📌 Data Dictionary Legend

- 🔑 = Primary Key
- 🔗 = Foreign Key
- N:1 = Many-to-One relationship
- 1:N = One-to-Many relationship

---

**Created:** December 31, 2025  
**Data Source:** SyntheticMass - Synthetic Healthcare Data  
**Sample Size:** 23 patients with complete medical histories
