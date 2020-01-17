/*
select
bc.[logid],
--bc.surgerydate as surgerydate_actual,
ef.patientencountercsnid as encounterid, 
ef.patientencountercsnid_actual as patientencountercsnid_actual, 
pim.randomnumber as studyid,
pim.identifier as patientid_actual,
pim.primarymrn,
pim.RandomNumber,
--pim.DateofBirth,
CONVERT(VARCHAR(10), pim.DateofBirth, 23),
pim.BaseDateNumber,
bc.[stpfilename]
from [edwards].[bedmaster_basecohort] bc 
left outer join rpt.[cdm_encounterfact_actual] ef on ef.patientencountercsnid_actual = bc.PatientEncounterCSNID
left outer join [dbo].[bedmaster_patientidentifiermap] pim on pim.randomnumber = ef.patientid
where pim.primaryMRN in ('4635037','5883791','4487595','4473298','2227725') 
-- logid in ('711744')
*/


select
bc.[logid],
--bc.surgerydate as surgerydate_actual,
im.RandomNUmber as encounterid,
ef.patientencountercsnid as patientencountercsnid_actual,
pim.randomnumber as studyid,
pim.identifier as patientid_actual,
pim.primarymrn,
pim.RandomNumber,
--pim.DateofBirth,
CONVERT(VARCHAR(10), pim.DateofBirth,23) as DateofBirth,
--SUBSTRING(pim.DateofBirth,1,10),
pim.BaseDateNumber,
bc.[stpfilename]
from [edwards].[basecohort] bc
    left outer join dbo.[cdm_encounterfact] ef on ef.patientencountercsnid = bc.PatientEncounterCSNID
    left outer join [dbo].[DDM_IdentifierMap] im on im.[Identifier] = ef.patientencountercsnid and im.idType = 123
    left outer join [dbo].[bedmaster_patientidentifiermap] pim on pim.identifier = ef.patientid
where pim.primaryMRN in ('4635037','5883791','4487595','4473298','2227725')
