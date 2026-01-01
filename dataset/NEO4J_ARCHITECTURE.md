# Neo4j Database Architecture for Healthcare Data

## 🎯 Overview

This document defines the complete Neo4j graph database architecture for the SyntheticMass healthcare dataset, including node types, relationships, properties, constraints, and data loading queries.

---

## 📊 Graph Schema Design

### Node Types (Labels)

We'll create **8 node types** representing the main entities:

```
(:Patient)
(:Encounter)
(:Reason)
(:Condition)
(:Medication)
(:Procedure)
(:Careplan)
(:Immunization)
(:Observation)
```

---

## 🏗️ Detailed Node Schemas

### 1. Patient Node
**Label:** `Patient`

**Properties:**
```cypher
{
  id: String (UNIQUE, INDEXED),
  birthDate: Date,
  deathDate: Date (nullable),
  ssn: String,
  prefix: String,
  firstName: String,
  lastName: String,
  suffix: String,
  marital: String,
  race: String,
  ethnicity: String,
  gender: String,
  birthPlace: String,
  address: String
}
```

**Constraints:**
```cypher
CREATE CONSTRAINT patient_id_unique IF NOT EXISTS
FOR (p:Patient) REQUIRE p.id IS UNIQUE;

CREATE INDEX patient_name_index IF NOT EXISTS
FOR (p:Patient) ON (p.lastName, p.firstName);
```

---

### 2. Encounter Node
**Label:** `Encounter`

**Properties:**
```cypher
{
  id: String (UNIQUE, INDEXED),
  date: Date,
  code: String,
  description: String
}
```

**Constraints:**
```cypher
CREATE CONSTRAINT encounter_id_unique IF NOT EXISTS
FOR (e:Encounter) REQUIRE e.id IS UNIQUE;

CREATE INDEX encounter_date_index IF NOT EXISTS
FOR (e:Encounter) ON (e.date);
```

---

### 3. Reason Node
**Label:** `Reason`

**Properties:**
```cypher
{
  code: String (UNIQUE, INDEXED),
  description: String
}
```

**Note:** Reasons are catalog entities (same reason can apply to multiple encounters)


---

### 4. Condition Node
**Label:** `Condition`

**Properties:**
```cypher
{
  code: String (INDEXED),
  description: String,
  startDate: Date,
  stopDate: Date (nullable)
}
```

**Note:** Conditions are shared entities (same condition can affect multiple patients)


---

### 5. Medication Node
**Label:** `Medication`

**Properties:**
```cypher
{
  code: String (INDEXED),
  description: String
}
```

**Note:** Medications are catalog entities (same drug can be prescribed to multiple patients)

**Constraints:**
```cypher
CREATE INDEX medication_code_index IF NOT EXISTS
FOR (m:Medication) ON (m.code);
```

---

### 6. Procedure Node
**Label:** `Procedure`

**Properties:**
```cypher
{
  code: String (INDEXED),
  description: String
}
```


---

### 7. Careplan Node
**Label:** `Careplan`

**Properties:**
```cypher
{
  id: String (UNIQUE),
  code: String,
  description: String,
  startDate: Date,
  stopDate: Date (nullable)
}
```

---

### 8. Immunization Node
**Label:** `Immunization`

**Properties:**
```cypher
{
  code: String (INDEXED),
  description: String
}
```

**Constraints:**
```cypher
CREATE INDEX immunization_code_index IF NOT EXISTS
FOR (i:Immunization) ON (i.code);
```

---

### 9. Observation Node
**Label:** `Observation`

**Properties:**
```cypher
{
  code: String (INDEXED),
  description: String
}
```


---

## 🔗 Relationship Types

### Graph Architecture

This graph follows an **encounter-centric model** where:
- Patients connect directly only to Encounters
- All clinical events (conditions, medications, procedures, etc.) are accessed through Encounters
- This eliminates redundancy and provides clear temporal context for all medical events

### Patient Relationships

#### 1. Patient → Encounter
```cypher
(:Patient)-[:HAD_ENCOUNTER]->(:Encounter)
```
- **Direction:** Patient to Encounter
- **Properties:** None needed (date is on Encounter node)
- **Cardinality:** One patient to many encounters
- **Note:** This is the ONLY direct relationship from Patient nodes

---

### Encounter Relationships (Clinical Events)

#### 2. Encounter → Reason
```cypher
(:Encounter)-[:HAS_REASON]->(:Reason)
```
- Links encounters to their documented reason/chief complaint
- **Direction:** Encounter to Reason
- **Cardinality:** Many-to-one (multiple encounters can have same reason)

---

#### 3. Encounter → Condition
```cypher
(:Encounter)-[:DIAGNOSED]->(:Condition)
```
- Tracks which conditions were diagnosed during which encounters
- **Properties:** `startDate`, `stopDate` for condition timeline

---

#### 4. Encounter → Medication
```cypher
(:Encounter)-[:PRESCRIBED_MEDICATION]->(:Medication)
```
- Links medications prescribed during encounters
- **Properties:** `startDate`, `stopDate`, `reasonCode`

---

#### 5. Encounter → Procedure
```cypher
(:Encounter)-[:PERFORMED]->(:Procedure)
```
- Links procedures performed during encounters
- **Properties:** `date`, `reasonCode`, `reasonDescription`

---

#### 6. Encounter → Immunization
```cypher
(:Encounter)-[:ADMINISTERED]->(:Immunization)
```
- Links immunizations administered during encounters
- **Properties:** `date`

---

#### 7. Encounter → Observation
```cypher
(:Encounter)-[:RECORDED]->(:Observation)
```
- Links observations recorded during encounters
- **Properties:** `date`, `value`, `units`

---

#### 8. Encounter → Careplan
```cypher
(:Encounter)-[:HAS_CAREPLAN]->(:Careplan)
```
- Links care plans created during encounters

---

### Treatment Relationships

#### 9. Medication → Condition
```cypher
(:Medication)-[:TREATS]->(:Condition)
```
- Links medications to the conditions they treat (via reasonCode)
- **Direction:** Medication to Condition
- **Properties:** None needed (the relationship itself carries meaning)

---

#### 10. Careplan → Reason
```cypher
(:Careplan)-[:FOR_REASON]->(:Reason)
```
- Links careplans to the medical reasons they address

---

## 🛠️ Setup Script

### Complete Cypher Script to Create Schema

```cypher
// ============================================
// NEO4J SCHEMA SETUP SCRIPT
// Healthcare Data Graph Database
// ============================================

// 1. CREATE CONSTRAINTS (for data integrity)
// ============================================

// Patient constraints
CREATE CONSTRAINT patient_id_unique IF NOT EXISTS
FOR (p:Patient) REQUIRE p.id IS UNIQUE;

// Encounter constraints
CREATE CONSTRAINT encounter_id_unique IF NOT EXISTS
FOR (e:Encounter) REQUIRE e.id IS UNIQUE;

// Medication constraints (catalog entity - unique by drug code)
CREATE CONSTRAINT medication_code_unique IF NOT EXISTS
FOR (m:Medication) REQUIRE m.code IS UNIQUE;

// Immunization constraints (catalog entity - unique by vaccine code)
CREATE CONSTRAINT immunization_code_unique IF NOT EXISTS
FOR (i:Immunization) REQUIRE i.code IS UNIQUE;

// Reason constraint
CREATE CONSTRAINT reason_code_unique IF NOT EXISTS
FOR (r:Reason) REQUIRE r.reasonCode IS UNIQUE;


// 2. CREATE INDEXES (for query performance)
// ============================================

// Patient indexes
CREATE INDEX patient_name_index IF NOT EXISTS
FOR (p:Patient) ON (p.lastName, p.firstName);

CREATE INDEX patient_birthdate_index IF NOT EXISTS
FOR (p:Patient) ON (p.birthDate);

// Encounter indexes
CREATE INDEX encounter_date_index IF NOT EXISTS
FOR (e:Encounter) ON (e.date);

CREATE INDEX encounter_code_index IF NOT EXISTS
FOR (e:Encounter) ON (e.code);

// Medication indexes
CREATE INDEX medication_code_index IF NOT EXISTS
FOR (m:Medication) ON (m.code);

// Immunization indexes
CREATE INDEX immunization_code_index IF NOT EXISTS
FOR (i:Immunization) ON (i.code);

// Reason indexe
CREATE INDEX reason_code_index IF NOT EXISTS
FOR (i:Reason) ON (i.reasonCode);

// 3. VERIFY SCHEMA
// ============================================

// Show all constraints
SHOW CONSTRAINTS;

// Show all indexes
SHOW INDEXES;
```

---

## 📥 Data Loading Strategy

### Loading Order (to maintain referential integrity)

**Encounter-Centric Model:** All clinical data flows through encounters, eliminating redundant patient relationships.

1. **Load Catalog Nodes** (entities without dependencies)
   - Reasons
   - Conditions
   - Medications
   - Procedures
   - Immunizations
   - Observations

2. **Load Core Entities**
   - Patients
   - Encounters

3. **Create Patient-Encounter Relationships**
   - Patient → Encounter (ONLY direct patient relationship)

4. **Create Encounter-Clinical Event Relationships**
   - Encounter → Reason
   - Encounter → Condition
   - Encounter → Medication
   - Encounter → Procedure
   - Encounter → Immunization
   - Encounter → Observation

5. **Load Time-based Entities**
   - Careplans

6. **Create Careplan Relationships**
   - Encounter → Careplan
   - Careplan → Reason

7. **Create Treatment Relationships**
   - Medication → Condition (TREATS)

---

## 📝 Sample Cypher Loading Queries

### 1. Load Patients

```cypher
// Using LOAD CSV
LOAD CSV WITH HEADERS FROM 'file:///sampled_patients.csv' AS row
CREATE (p:Patient {
  id: row.ID,
  birthDate: date(row.BIRTHDATE),
  deathDate: CASE WHEN row.DEATHDATE IS NOT NULL THEN date(row.DEATHDATE) ELSE null END,
  ssn: row.SSN,
  prefix: row.PREFIX,
  firstName: row.FIRST,
  lastName: row.LAST,
  suffix: row.SUFFIX,
  marital: row.MARITAL,
  race: row.RACE,
  ethnicity: row.ETHNICITY,
  gender: row.GENDER,
  birthPlace: row.BIRTHPLACE,
  address: row.ADDRESS
});
```

### 2. Load Conditions (Catalog)

```cypher
// First, create unique Condition nodes (catalog)
LOAD CSV WITH HEADERS FROM 'file:///sampled_conditions.csv' AS row
MERGE (c:Condition {code: row.CODE})
ON CREATE SET c.description = row.DESCRIPTION;
```

### 3. Create Encounter-Condition Relationships

```cypher
// Link conditions to encounters (NO direct patient relationships)
LOAD CSV WITH HEADERS FROM 'file:///sampled_conditions.csv' AS row
MATCH (e:Encounter {id: row.ENCOUNTER})
MATCH (c:Condition {code: row.CODE})
CREATE (e)-[:DIAGNOSED {
  startDate: date(row.START),
  stopDate: CASE WHEN row.STOP IS NOT NULL AND row.STOP <> '' THEN date(row.STOP) ELSE null END
}]->(c);
```

### 4. Load Reasons (Catalog)

```cypher
// Create unique Reason nodes (catalog)
LOAD CSV WITH HEADERS FROM 'file:///sampled_encounters.csv' AS row
WITH row WHERE row.REASONCODE IS NOT NULL AND row.REASONCODE <> ''
MERGE (r:Reason {code: row.REASONCODE})
ON CREATE SET r.description = row.REASONDESCRIPTION;
```

### 5. Load Encounters

```cypher
// Create Encounter nodes (without reason - now in separate node)
LOAD CSV WITH HEADERS FROM 'file:///sampled_encounters.csv' AS row
CREATE (e:Encounter {
  id: row.ID,
  date: date(row.DATE),
  code: row.CODE,
  description: row.DESCRIPTION
});

// Create Patient-Encounter relationships (ONLY direct patient relationship)
LOAD CSV WITH HEADERS FROM 'file:///sampled_encounters.csv' AS row
MATCH (p:Patient {id: row.PATIENT})
MATCH (e:Encounter {id: row.ID})
CREATE (p)-[:HAD_ENCOUNTER]->(e);

// Create Encounter-Reason relationships
LOAD CSV WITH HEADERS FROM 'file:///sampled_encounters.csv' AS row
WITH row WHERE row.REASONCODE IS NOT NULL AND row.REASONCODE <> ''
MATCH (e:Encounter {id: row.ID})
MATCH (r:Reason {code: row.REASONCODE})
CREATE (e)-[:HAS_REASON]->(r);
```

### 6. Load Medications

```cypher
// Create Medication catalog nodes
LOAD CSV WITH HEADERS FROM 'file:///sampled_medications.csv' AS row
MERGE (m:Medication {code: row.CODE})
ON CREATE SET m.description = row.DESCRIPTION;

// Create Encounter-Medication relationships (NO patient relationships)
LOAD CSV WITH HEADERS FROM 'file:///sampled_medications.csv' AS row
MATCH (e:Encounter {id: row.ENCOUNTER})
MATCH (m:Medication {code: row.CODE})
CREATE (e)-[:PRESCRIBED_MEDICATION {
  startDate: date(row.START),
  stopDate: CASE WHEN row.STOP IS NOT NULL AND row.STOP <> '' THEN date(row.STOP) ELSE null END,
  reasonCode: row.REASONCODE
}]->(m);

// Create Medication-Condition TREATS relationships
LOAD CSV WITH HEADERS FROM 'file:///sampled_medications.csv' AS row
WITH row WHERE row.REASONCODE IS NOT NULL AND row.REASONCODE <> ''
MATCH (m:Medication {code: row.CODE})
MATCH (c:Condition {code: toInteger(toFloat(row.REASONCODE))})
MERGE (m)-[:TREATS]->(c);
```

### 7. Load Procedures

```cypher
// Create Procedure catalog
LOAD CSV WITH HEADERS FROM 'file:///sampled_procedures.csv' AS row
MERGE (proc:Procedure {code: row.CODE})
ON CREATE SET proc.description = row.DESCRIPTION;

// Create Encounter-Procedure relationships (NO patient relationships)
LOAD CSV WITH HEADERS FROM 'file:///sampled_procedures.csv' AS row
MATCH (e:Encounter {id: row.ENCOUNTER})
MATCH (proc:Procedure {code: row.CODE})
CREATE (e)-[:PERFORMED {
  date: date(row.DATE),
  reasonCode: row.REASONCODE,
  reasonDescription: row.REASONDESCRIPTION
}]->(proc);
```

### 8. Load Immunizations

```cypher
// Create Immunization catalog
LOAD CSV WITH HEADERS FROM 'file:///sampled_immunizations.csv' AS row
MERGE (i:Immunization {code: row.CODE})
ON CREATE SET i.description = row.DESCRIPTION;

// Create Encounter-Immunization relationships (NO patient relationships)
LOAD CSV WITH HEADERS FROM 'file:///sampled_immunizations.csv' AS row
MATCH (e:Encounter {id: row.ENCOUNTER})
MATCH (i:Immunization {code: row.CODE})
CREATE (e)-[:ADMINISTERED {
  date: date(row.DATE)
}]->(i);
```

### 9. Load Observations

```cypher
// Create Observation catalog
LOAD CSV WITH HEADERS FROM 'file:///sampled_observations.csv' AS row
MERGE (o:Observation {code: row.CODE})
ON CREATE SET o.description = row.DESCRIPTION;

// Create Encounter-Observation relationships (NO patient relationships)
LOAD CSV WITH HEADERS FROM 'file:///sampled_observations.csv' AS row
MATCH (e:Encounter {id: row.ENCOUNTER})
MATCH (o:Observation {code: row.CODE})
CREATE (e)-[:RECORDED {
  date: date(row.DATE),
  value: row.VALUE,
  units: row.UNITS
}]->(o);
```

### 10. Load Careplans

```cypher
// Step 1: Create unique Reason nodes (catalog entities)
LOAD CSV WITH HEADERS FROM 'file:///sampled_data/sampled_careplans.csv' AS row
WITH row WHERE row.REASONCODE IS NOT NULL
MERGE (r:Reason {code: row.REASONCODE})
ON CREATE SET r.description = row.REASONDESCRIPTION;
// Step 2: Create CarePlan nodes with properties
LOAD CSV WITH HEADERS FROM 'file:///sampled_data/sampled_careplans.csv' AS row
MERGE (cp:Careplan {id: row.ID})
ON CREATE SET
  cp.code = row.CODE,
  cp.description = row.DESCRIPTION,
  cp.start = date(row.START),
  cp.stop = CASE WHEN row.STOP IS NOT NULL THEN date(row.STOP) ELSE null END;

// Step 3: Create relationships between CarePlan and Encounter
LOAD CSV WITH HEADERS FROM 'file:///sampled_data/sampled_careplans.csv' AS row
MATCH (cp:Careplan {id: row.ID})
MATCH (e:Encounter {id: row.ENCOUNTER})
MERGE (e)-[:HAS_CAREPLAN]->(cp);

// Step 4: Create relationships between CarePlan and Reason
LOAD CSV WITH HEADERS FROM 'file:///sampled_data/sampled_careplans.csv' AS row
WHERE row.REASONCODE IS NOT NULL
MATCH (cp:Careplan {id: row.ID})
MATCH (r:Reason {code: row.REASONCODE})
MERGE (cp)-[:FOR_REASON]->(r);

```