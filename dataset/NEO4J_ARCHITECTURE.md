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

### Patient-Centric Relationships

#### 1. Patient → Encounter
```cypher
(:Patient)-[:HAD_ENCOUNTER {date: Date}]->(:Encounter)
```
- **Direction:** Patient to Encounter
- **Properties:** `date` (when the encounter occurred)
- **Cardinality:** One patient to many encounters

---

#### 2. Patient → Condition
```cypher
(:Patient)-[:HAS_CONDITION {
  startDate: Date,
  stopDate: Date (nullable),
  diagnosedAt: String (encounter_id)
}]->(:Condition)
```
- **Direction:** Patient to Condition
- **Properties:** 
  - `startDate`: When condition started
  - `stopDate`: When condition ended (null if ongoing)
  - `diagnosedAt`: Encounter ID where diagnosed
- **Cardinality:** Many-to-many

---

#### 3. Patient → Medication
```cypher
(:Patient)-[:PRESCRIBED {
  startDate: Date,
  stopDate: Date (nullable),
  prescribedAt: String (encounter_id),
  reasonCode: String (nullable)
}]->(:Medication)
```
- **Direction:** Patient to Medication
- **Properties:**
  - `startDate`, `stopDate`: Duration of prescription
  - `prescribedAt`: Encounter where prescribed
  - `reasonCode`: Condition code it treats
- **Cardinality:** Many-to-many

---

#### 4. Patient → Procedure
```cypher
(:Patient)-[:UNDERWENT {
  date: Date,
  encounterId: String,
  reasonCode: String (nullable),
  reasonDescription: String (nullable)
}]->(:Procedure)
```
- **Direction:** Patient to Procedure
- **Properties:**
  - `date`: When performed
  - `encounterId`: Where performed
  - `reasonCode`, `reasonDescription`: Why performed

---

#### 5. Patient → Careplan
```cypher
(:Patient)-[:ENROLLED_IN {
  id: String,
  startDate: Date,
  stopDate: Date (nullable),
  encounterId: String,
  reasonCode: String (nullable),
  reasonDescription: String (nullable)
}]->(:Careplan)
```

---

#### 6. Patient → Immunization
```cypher
(:Patient)-[:RECEIVED {
  date: Date,
  encounterId: String
}]->(:Immunization)
```

---

#### 7. Patient → Observation
```cypher
(:Patient)-[:HAD_OBSERVATION {
  date: Date,
  encounterId: String,
  value: String (nullable),
  units: String (nullable)
}]->(:Observation)
```

---

### Encounter Relationships

#### 8. Encounter → Reason
```cypher
(:Encounter)-[:HAS_REASON]->(:Reason)
```
- Links encounters to their documented reason/chief complaint
- **Direction:** Encounter to Reason
- **Cardinality:** Many-to-one (multiple encounters can have same reason)

---

#### 9. Encounter → Condition
```cypher
(:Encounter)-[:DIAGNOSED]->(:Condition)
```
- Tracks which conditions were diagnosed during which encounters

---

#### 10. Encounter → Medication
```cypher
(:Encounter)-[:PRESCRIBED_MEDICATION]->(:Medication)
```

---

#### 11. Encounter → Procedure
```cypher
(:Encounter)-[:PERFORMED]->(:Procedure)
```

---

#### 12. Encounter → Immunization
```cypher
(:Encounter)-[:ADMINISTERED]->(:Immunization)
```

---

#### 13. Encounter → Observation
```cypher
(:Encounter)-[:RECORDED]->(:Observation)
```

---

### Treatment Relationships

#### 14. Medication → Condition
```cypher
(:Medication)-[:TREATS]->(:Condition)
```
- Links medications to the conditions they treat (via reasonCode)
- **Direction:** Medication to Condition
- **Properties:** None needed (the relationship itself carries meaning)

---

#### 15. Careplan → Condition
```cypher
(:Careplan)-[:MANAGES]->(:Condition)
```
- Links careplans to conditions they manage

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

3. **Load Time-based Entities**
   - Careplans

4. **Create Patient Relationships**
   - Patient → Condition
   - Patient → Medication
   - Patient → Procedure
   - Patient → Immunization
   - Patient → Observation
   - Patient → Encounter
   - Patient → Careplan

5. **Create Encounter Relationships**
   - Encounter → Condition
   - Encounter → Medication
   - Encounter → Procedure
   - Encounter → Immunization
   - Encounter → Observation

6. **Create Treatment Relationship**
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

### 3. Create Patient-Condition Relationships

```cypher
LOAD CSV WITH HEADERS FROM 'file:///sampled_conditions.csv' AS row
MATCH (p:Patient {id: row.PATIENT})
MATCH (c:Condition {code: row.CODE})
CREATE (p)-[:HAS_CONDITION {
  startDate: date(row.START),
  stopDate: CASE WHEN row.STOP IS NOT NULL AND row.STOP <> '' THEN date(row.STOP) ELSE null END,
  diagnosedAt: row.ENCOUNTER
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

// Create Patient-Encounter relationships
LOAD CSV WITH HEADERS FROM 'file:///sampled_encounters.csv' AS row
MATCH (p:Patient {id: row.PATIENT})
MATCH (e:Encounter {id: row.ID})
CREATE (p)-[:HAD_ENCOUNTER {date: date(row.DATE)}]->(e);

// Create Encounter-Reason relationships
LOAD CSV WITH HEADERS FROM 'file:///sampled_encounters.csv' AS row
WITH row WHERE row.REASONCODE IS NOT NULL AND row.REASONCODE <> ''
MATCH (e:Encounter {id: row.ID})
MATCH (r:Reason {code: row.REASONCODE})
CREATE (e)-[:HAS_REASON]->(r);

// Create Encounter-Condition relationships
LOAD CSV WITH HEADERS FROM 'file:///sampled_conditions.csv' AS row
MATCH (e:Encounter {id: row.ENCOUNTER})
MATCH (c:Condition {code: row.CODE})
CREATE (e)-[:DIAGNOSED]->(c);
```

### 6. Load Medications

```cypher
// Create Medication catalog nodes
LOAD CSV WITH HEADERS FROM 'file:///sampled_medications.csv' AS row
MERGE (m:Medication {code: row.CODE})
ON CREATE SET m.description = row.DESCRIPTION;

// Create Patient-Medication relationships
LOAD CSV WITH HEADERS FROM 'file:///sampled_medications.csv' AS row
MATCH (p:Patient {id: row.PATIENT})
MATCH (m:Medication {code: row.CODE})
CREATE (p)-[:PRESCRIBED {
  startDate: date(row.START),
  stopDate: CASE WHEN row.STOP IS NOT NULL AND row.STOP <> '' THEN date(row.STOP) ELSE null END,
  prescribedAt: row.ENCOUNTER,
  reasonCode: row.REASONCODE
}]->(m);

// Create Medication-Condition TREATS relationships
LOAD CSV WITH HEADERS FROM 'file:///sampled_medications.csv' AS row
WITH row WHERE row.REASONCODE IS NOT NULL AND row.REASONCODE <> ''
MATCH (m:Medication {code: row.CODE})
MATCH (c:Condition {code: toInteger(toFloat(row.REASONCODE))})
MERGE (m)-[:TREATS]->(c);

// Create Encounter-Medication relationships
LOAD CSV WITH HEADERS FROM 'file:///sampled_medications.csv' AS row
MATCH (e:Encounter {id: row.ENCOUNTER})
MATCH (m:Medication {code: row.CODE})
CREATE (e)-[:PRESCRIBED_MEDICATION]->(m);
```

### 7. Load Procedures

```cypher
// Create Procedure catalog
LOAD CSV WITH HEADERS FROM 'file:///sampled_procedures.csv' AS row
MERGE (proc:Procedure {code: row.CODE})
ON CREATE SET proc.description = row.DESCRIPTION;

// Create Patient-Procedure relationships
LOAD CSV WITH HEADERS FROM 'file:///sampled_procedures.csv' AS row
MATCH (p:Patient {id: row.PATIENT})
MATCH (proc:Procedure {code: row.CODE})
CREATE (p)-[:UNDERWENT {
  date: date(row.DATE),
  encounterId: row.ENCOUNTER,
  reasonCode: row.REASONCODE,
  reasonDescription: row.REASONDESCRIPTION
}]->(proc);

// Create Encounter-Procedure relationships
LOAD CSV WITH HEADERS FROM 'file:///sampled_procedures.csv' AS row
MATCH (e:Encounter {id: row.ENCOUNTER})
MATCH (proc:Procedure {code: row.CODE})
CREATE (e)-[:PERFORMED]->(proc);
```

### 8. Load Immunizations

```cypher
// Create Immunization catalog
LOAD CSV WITH HEADERS FROM 'file:///sampled_immunizations.csv' AS row
MERGE (i:Immunization {code: row.CODE})
ON CREATE SET i.description = row.DESCRIPTION;

// Create Patient-Immunization relationships
LOAD CSV WITH HEADERS FROM 'file:///sampled_immunizations.csv' AS row
MATCH (p:Patient {id: row.PATIENT})
MATCH (i:Immunization {code: row.CODE})
CREATE (p)-[:RECEIVED {
  date: date(row.DATE),
  encounterId: row.ENCOUNTER
}]->(i);


// Create Encounter-Immunization relationships
LOAD CSV WITH HEADERS FROM 'file:///sampled_immunizations.csv' AS row
MATCH (e:Encounter {id: row.ENCOUNTER})
MATCH (i:Immunization {code: row.CODE})
CREATE (e)-[:ADMINISTERED]->(i);
```

### 9. Load Observations

```cypher
// Create Observation catalog
LOAD CSV WITH HEADERS FROM 'file:///sampled_observations.csv' AS row
MERGE (o:Observation {code: row.CODE})
ON CREATE SET o.description = row.DESCRIPTION;

// Create Patient-Observation relationships
LOAD CSV WITH HEADERS FROM 'file:///sampled_observations.csv' AS row
MATCH (p:Patient {id: row.PATIENT})
MATCH (o:Observation {code: row.CODE})
CREATE (p)-[:HAD_OBSERVATION {
  date: date(row.DATE),
  encounterId: row.ENCOUNTER,
  value: row.VALUE,
  units: row.UNITS
}]->(o);


// Create Encounter-Observation relationships
LOAD CSV WITH HEADERS FROM 'file:///sampled_observations.csv' AS row
MATCH (e:Encounter {id: row.ENCOUNTER})
MATCH (o:Observation {code: row.CODE})
CREATE (e)-[:RECORDED]->(o);
```

### 10. Load Careplans

```cypher
// Create Careplan catalog nodes
LOAD CSV WITH HEADERS FROM 'file:///sampled_careplans.csv' AS row
MERGE (cp:Careplan {code: row.CODE})
ON CREATE SET cp.description = row.DESCRIPTION;

// Create Patient-Careplan relationships
LOAD CSV WITH HEADERS FROM 'file:///sampled_careplans.csv' AS row
MATCH (p:Patient {id: row.PATIENT})
MATCH (cp:Careplan {code: row.CODE})
CREATE (p)-[:ENROLLED_IN {
  id: row.ID,
  startDate: date(row.START),
  stopDate: CASE WHEN row.STOP IS NOT NULL AND row.STOP <> '' THEN date(row.STOP) ELSE null END,
  encounterId: row.ENCOUNTER,
  reasonCode: row.REASONCODE,
  reasonDescription: row.REASONDESCRIPTION
}]->(cp);


```

---

## 🔍 Useful Queries After Loading

### Check Node Counts
```cypher
MATCH (n) RETURN labels(n)[0] AS NodeType, count(n) AS Count
ORDER BY Count DESC;
```

### Check Relationship Counts
```cypher
MATCH ()-[r]->() RETURN type(r) AS RelationType, count(r) AS Count
ORDER BY Count DESC;
```

### Get Complete Patient Graph
```cypher
MATCH path = (p:Patient {id: 'abf03ea9-2d1b-414e-8b07-5087c44bac8a'})-[*1..2]-()
RETURN path
LIMIT 100;
```

### Find Medication Treatment Chains
```cypher
MATCH (p:Patient)-[:PRESCRIBED]->(m:Medication)-[:TREATS]->(c:Condition)
RETURN p.firstName, p.lastName, m.description, c.description
LIMIT 20;
```

---

## 📋 Pre-Loading Checklist

- [ ] Neo4j database is running
- [ ] CSV files are in the Neo4j import directory (typically `/var/lib/neo4j/import/`)
- [ ] All constraints are created
- [ ] All indexes are created
- [ ] CSV files have proper headers
- [ ] Date formats are consistent (YYYY-MM-DD)
- [ ] Backup plan in place



**Ready to load data!** 🚀

Next steps:
1. Run the schema setup script
2. Copy CSV files to Neo4j import directory
3. Execute loading queries in order
4. Verify with count queries