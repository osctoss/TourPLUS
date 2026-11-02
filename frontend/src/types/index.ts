export type UserRole = 'PATIENT' | 'ADMIN' | 'DATA_CURATOR';

export interface User {
  id: string;
  email: string;
  role: UserRole;
  is_verified: boolean;
}

export interface PatientProfile {
  id: string;
  full_name: string;
  phone_number?: string;
  nationality?: string;
  residence_country?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  passport_number_masked?: string;
}

export interface Specialty {
  id: string;
  name: string;
  slug: string;
  description: string;
}

export interface TreatmentCategory {
  id: string;
  specialty: string;
  name: string;
  slug: string;
  description: string;
}

export interface Hospital {
  id: string;
  name: string;
  slug: string;
  description: string;
  city_name: string;
  state_name: string;
  country_name: string;
  address: string;
  latitude: number | null;
  longitude: number | null;
  international_patient_support: boolean;
  verification_status: 'VERIFIED' | 'INDICATIVE' | 'PENDING_REVIEW';
  data_classification: 'VERIFIED' | 'INDICATIVE' | 'DEMO';
}

export interface ScenarioBudgetLine {
  id: string;
  expense_category: 'TREATMENT' | 'INTERNATIONAL_FLIGHT' | 'ACCOMMODATION' | 'VISA' | 'LOCAL_TRANSPORT' | 'MISCELLANEOUS';
  description: string;
  min_amount: string;
  expected_amount: string;
  max_amount: string;
  source_currency: string;
  scenario_currency: string;
  converted_expected_amount: string;
  quantity: string;
  unit: string;
  data_classification: string;
}

export interface DestinationRecommendation {
  id: string;
  destination_id: string;
  destination_name: string;
  city_name: string;
  tourism_scope: 'LOCAL_REGIONAL' | 'STATE_LEVEL' | 'NATIONAL';
  rank: number;
  interest_score: string;
  geography_score: string;
  cost_score: string;
  data_confidence_score: string;
  recovery_review_status: string;
  feasibility_status: 'FEASIBLE' | 'REQUIRES_CLINICAL_REVIEW' | 'INELIGIBLE';
  estimated_visit_cost: string;
  estimated_route_cost: string;
  estimated_route_duration: number;
  explanation: string;
}

export interface PackageMatch {
  id: string;
  travel_package_id: string;
  package_name: string;
  agency_name: string;
  rank: number;
  destination_coverage_score: string;
  inclusion_credit: string;
  listed_package_price: string;
  effective_incremental_cost: string;
  remaining_discretionary_budget: string;
  budget_feasibility_status: 'FEASIBLE' | 'OVER_BUDGET';
  itinerary_fit_score: string;
  overall_score: string;
  explanation: string;
}

export interface HospitalScenario {
  id: string;
  recommendation_run_id: string;
  hospital_id: string;
  hospital_name: string;
  city_name: string;
  treatment_name: string;
  rank: number;
  ranking_score: string;
  scenario_currency: string;
  verification_status: string;
  data_classification: string;
  budget_lines?: ScenarioBudgetLine[];
  destinations?: DestinationRecommendation[];
  package_matches?: PackageMatch[];
}

export interface FinalPlan {
  id: string;
  plan_title: string;
  hospital_scenario: HospitalScenario;
  package_match?: PackageMatch | null;
  selected_scope: string;
  status: 'DRAFT' | 'CONFIRMED' | 'ARCHIVED';
  created_at: string;
  destinations?: Array<{
    destination_id: string;
    destination_name: string;
    sequence_order: number;
  }>;
}

