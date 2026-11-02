# Security, Privacy & Compliance — TourPlus AI

## 1. Authentication & Object-Level Authorization
- **Custom User Model**: Primary keys are non-sequential UUIDv4 to prevent enumeration attacks.
- **Strict Object Ownership**: All patient records (TripRequests, RecommendationRuns, Scenarios, FinalPlans) enforce object-level permission checks (`IsOwner`), preventing Patient A from viewing or modifying Patient B's medical requests.

## 2. Data Minimization & Protected Health Information (PHI)
- TourPlus AI does **not** store sensitive medical records, imaging (DICOM/X-ray), or raw clinical charts.
- Patient health input is restricted to selected specialty, treatment procedure, and non-identifying doctor guidance notes.
- Passwords are encrypted using Django's PBKDF2 with SHA-256 hash.

## 3. Disclaimers & Regulatory Protection
- **Medical Disclaimer**: Placed prominently on the landing page, assessment wizard, scenario results, and printed final plan. Clearly states that TourPlus AI provides non-clinical decision support only and that treating clinicians must approve all medical travel and recovery plans.
- **Financial Disclaimer**: Identifies indicative cost ranges and explains that actual hospital invoices depend on diagnostic evaluation upon arrival.

