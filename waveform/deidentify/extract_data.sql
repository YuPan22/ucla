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
