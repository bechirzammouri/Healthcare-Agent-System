# Cypher Test Queries

Quick test queries to verify your Neo4j graph database is loaded correctly.

---

## 1. Basic Node Count Tests

### Count all nodes by type
```cypher
MATCH (n) 
RETURN labels(n)[0] AS NodeType, count(n) AS Count
ORDER BY Count DESC;
```

### Count Patients
```cypher
MATCH (p:Patient) 
RETURN count(p) AS TotalPatients;
```

### Count Encounters
```cypher
MATCH (e:Encounter) 
RETURN count(e) AS TotalEncounters;
```

### Count Conditions
```cypher
MATCH (c:Condition) 
RETURN count(c) AS TotalConditions;
```

### Count Medications
```cypher
MATCH (m:Medication) 
RETURN count(m) AS TotalMedications;
```

---

## 2. Basic Relationship Count Tests

### Count all relationships by type
```cypher
MATCH ()-[r]->() 
RETURN type(r) AS RelationType, count(r) AS Count
ORDER BY Count DESC;
```

### Count Patient-Encounter relationships
```cypher
MATCH (:Patient)-[r:HAD_ENCOUNTER]->(:Encounter) 
RETURN count(r) AS TotalEncounterRelationships;
```

### Count Patient-Condition relationships
```cypher
MATCH (:Patient)-[r:HAS_CONDITION]->(:Condition) 
RETURN count(r) AS TotalConditionRelationships;
```

---

## 3. Sample Data Tests

### Get 5 sample patients
```cypher
MATCH (p:Patient) 
RETURN p.id, p.firstName, p.lastName, p.gender, p.birthDate
LIMIT 5;
```

### Get 5 sample encounters with dates
```cypher
MATCH (e:Encounter) 
RETURN e.id, e.date, e.description
ORDER BY e.date DESC
LIMIT 5;
```

### Get 5 sample conditions
```cypher
MATCH (c:Condition) 
RETURN c.code, c.description
LIMIT 5;
```

---

## 4. Relationship Verification Tests

### Check if Patient-Encounter relationships exist
```cypher
MATCH (p:Patient)-[r:HAD_ENCOUNTER]->(e:Encounter)
RETURN p.firstName, p.lastName, e.date, e.description
LIMIT 5;
```

### Check if Medication-Condition TREATS relationships exist
```cypher
MATCH (m:Medication)-[r:TREATS]->(c:Condition)
RETURN m.description AS Medication, c.description AS TreatsCondition
LIMIT 10;
```

### Check if Encounter-Condition relationships exist
```cypher
MATCH (e:Encounter)-[r:DIAGNOSED]->(c:Condition)
RETURN e.date, e.description AS Encounter, c.description AS Diagnosed
LIMIT 5;
```

---

## 5. Patient Timeline Tests

### Get one patient's complete encounter history
```cypher
MATCH (p:Patient {id: 'e95be51d-44e6-48c5-8668-459892a0f5eb'})-[:HAD_ENCOUNTER]->(e:Encounter)
RETURN e.date, e.description, e.reasonCode
ORDER BY e.date DESC;
```
```cypher
MATCH (p:Patient {id: 'e95be51d-44e6-48c5-8668-459892a0f5eb'})-[:HAD_ENCOUNTER]->(e:Encounter)
RETURN e.date AS Date, e.description AS EncounterType, e.reasonCode AS ReasonCode
ORDER BY e.date DESC;
```

**Sample Result:**
| Date | EncounterType | ReasonCode |
|------|---------------|-----------|
| 2012-06-06 | Outpatient Encounter | null |
| 2012-06-06 | Death Certification | null |
| 2011-07-26 | Outpatient Encounter | null |
| 2010-08-13 | Outpatient Encounter | null |

### Get one patient with all their conditions
```cypher
MATCH (p:Patient)-[r:HAS_CONDITION]->(c:Condition)
WHERE p.id = 'dce0e825-07c6-428a-adba-5fbca33871d8'
RETURN p.firstName, p.lastName, 
       c.description, r.startDate, r.stopDate
ORDER BY r.startDate DESC;
```
**Sample Result:**
| First Name | Last Name | Condition | Start Date | Stop Date | 
|------------|-----------|-----------|------------|-----------|
| Lea427 | Braun385 | Viral sinusitis (disorder) | 2012-05-12 | 2012-05-31 |
| Lea427 | Braun385 | Fracture of ankle | 2010-07-09 | 2010-10-22 | 
| Lea427 | Braun385 | Prediabetes | 1987-06-02 | null |
---

## 6. Find Test Patient IDs

### Get patient IDs to use in other tests
```cypher
MATCH (p:Patient)-[:HAD_ENCOUNTER]->(e:Encounter)
WITH p, count(e) as encounterCount
WHERE encounterCount > 3
RETURN p.id, p.firstName, p.lastName, encounterCount
ORDER BY encounterCount DESC
LIMIT 5;
```

### Get a patient with medications
```cypher
MATCH (p:Patient)-[:PRESCRIBED]->(m:Medication)
WITH p, count(m) as medCount
WHERE medCount > 0
RETURN p.id, p.firstName, p.lastName, medCount
LIMIT 5;
```

---

## 7. Data Quality Tests

### Check for patients without encounters
```cypher
MATCH (p:Patient)
WHERE NOT (p)-[:HAD_ENCOUNTER]->()
RETURN count(p) AS PatientsWithoutEncounters;
```
Result : **5 patients**

### Check for encounters without patients
```cypher
MATCH (e:Encounter)
WHERE NOT ()-[:HAD_ENCOUNTER]->(e)
RETURN count(e) AS OrphanEncounters;
```
Result : 0 as expected
### Check for null dates
```cypher
MATCH (e:Encounter)
WHERE e.date IS NULL
RETURN count(e) AS EncountersWithoutDates;
```
Result : 0

---

## 8. Common Patterns Tests

### Most common conditions
```cypher
MATCH (c:Condition)<-[:HAS_CONDITION]-()
RETURN c.code, c.description, count(*) AS PatientCount
ORDER BY PatientCount DESC
LIMIT 10;
```
Most common condition is **Prediabetes** (9  patients out of 23)

### Most prescribed medications
```cypher
MATCH (m:Medication)<-[:PRESCRIBED]-()
RETURN m.code, m.description, count(*) AS PrescriptionCount
ORDER BY PrescriptionCount DESC
LIMIT 10;
```
Result : **Clopidogrel 75 MG Oral Tablet** ( 12 patients )
### Most common encounter types
```cypher
MATCH (e:Encounter)
RETURN e.code, e.description, count(*) AS EncounterCount
ORDER BY EncounterCount DESC
LIMIT 10;
```
**Result :** 
| Code | Description | Encounter Count |
|------|-------------|-----------------|
| 185349003 | Outpatient Encounter | 32 |
| 308646001 | Death Certification | 13 |
| 184347001 | Encounter for problem | 11 |
| 266707007 | Drug addiction therapy | 8 |
| 185345009 | Encounter for symptom | 7 |
---




If all tests pass, your database is ready for agent development! 🚀
