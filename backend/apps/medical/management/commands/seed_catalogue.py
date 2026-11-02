import decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.geography.models import Country, State, City, DataSource, ExchangeRate
from apps.medical.models import Specialty, TreatmentCategory
from apps.hospitals.models import (
    Hospital, HospitalSpecialty, HospitalTreatmentOffering,
    TreatmentCostEstimate, DataClassification, VerificationStatus
)
from apps.tourism.models import (
    DestinationCategory, TouristDestination, DestinationCategoryLink,
    DestinationCostEstimate
)
from apps.agencies.models import TravelAgency
from apps.packages.models import TravelPackage, PackageDestination, PackageInclusion
from apps.audit.models import RecommendationConfiguration


class Command(BaseCommand):
    help = 'Seeds initial curated medical tourism catalogue (Specialties, Hospitals, Destinations, Packages)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Beginning idempotent catalogue seeding..."))

        # 1. Countries
        india, _ = Country.objects.update_or_create(
            iso2='IN',
            defaults={'name': 'India', 'iso3': 'IND', 'default_currency': 'INR', 'is_active': True}
        )
        uk, _ = Country.objects.update_or_create(
            iso2='GB',
            defaults={'name': 'United Kingdom', 'iso3': 'GBR', 'default_currency': 'GBP', 'is_active': True}
        )
        usa, _ = Country.objects.update_or_create(
            iso2='US',
            defaults={'name': 'United States', 'iso3': 'USA', 'default_currency': 'USD', 'is_active': True}
        )
        uae, _ = Country.objects.update_or_create(
            iso2='AE',
            defaults={'name': 'United Arab Emirates', 'iso3': 'ARE', 'default_currency': 'AED', 'is_active': True}
        )

        # 2. States & Major Hospital Cities in India
        states_data = [
            ('Delhi NCR', 'DL', [
                ('New Delhi', 28.6139, 77.2090),
            ]),
            ('Haryana', 'HR', [
                ('Gurugram', 28.4595, 77.0266),
            ]),
            ('Maharashtra', 'MH', [
                ('Mumbai', 19.0760, 72.8777),
            ]),
            ('Tamil Nadu', 'TN', [
                ('Chennai', 13.0827, 80.2707),
                ('Mahabalipuram', 12.6269, 80.1927),
            ]),
            ('Karnataka', 'KA', [
                ('Bengaluru', 12.9716, 77.5946),
            ]),
            ('Telangana', 'TG', [
                ('Hyderabad', 17.3850, 78.4867),
            ]),
            ('West Bengal', 'WB', [
                ('Kolkata', 22.5726, 88.3639),
            ]),
            ('Kerala', 'KL', [
                ('Kochi', 9.9312, 76.2673),
                ('Alleppey', 9.4981, 76.3388),
            ]),
            ('Gujarat', 'GJ', [
                ('Ahmedabad', 23.0225, 72.5714),
            ]),
            ('Uttar Pradesh', 'UP', [
                ('Agra', 27.1767, 78.0081),
                ('Varanasi', 25.3176, 82.9739),
            ]),
            ('Rajasthan', 'RJ', [
                ('Jaipur', 26.9124, 75.7873),
            ]),
            ('Goa', 'GA', [
                ('Panaji', 15.4909, 73.8278),
            ]),
        ]

        cities_map = {}
        for state_name, state_code, cities in states_data:
            state_obj, _ = State.objects.update_or_create(
                country=india, name=state_name,
                defaults={'code': state_code}
            )
            for city_name, lat, lng in cities:
                city_obj, _ = City.objects.update_or_create(
                    state=state_obj, name=city_name,
                    defaults={'latitude': lat, 'longitude': lng, 'is_active': True}
                )
                cities_map[city_name] = city_obj

        # 3. Data Sources
        source_nha, _ = DataSource.objects.update_or_create(
            source_name='National Health Authority & NABH Registry',
            defaults={
                'publisher': 'Government of India',
                'source_url': 'https://nabh.co',
                'source_type': 'REGULATORY_PORTAL',
                'reliability_level': DataSource.Reliability.AUTHORITATIVE
            }
        )
        source_tourism, _ = DataSource.objects.update_or_create(
            source_name='Incredible India Tourism Registry',
            defaults={
                'publisher': 'Ministry of Tourism, India',
                'source_url': 'https://www.incredibleindia.org',
                'source_type': 'OFFICIAL_PORTAL',
                'reliability_level': DataSource.Reliability.AUTHORITATIVE
            }
        )
        source_benchmark, _ = DataSource.objects.update_or_create(
            source_name='Indo-Global Medical Tourism Benchmark 2026',
            defaults={
                'publisher': 'Healthcare Tourism Council',
                'source_type': 'BENCHMARK_SCHEDULE',
                'reliability_level': DataSource.Reliability.PROVIDER_PUBLISHED
            }
        )

        # 4. Exchange Rates
        rates = [
            ('USD', 'INR', decimal.Decimal('86.500000')),
            ('GBP', 'USD', decimal.Decimal('1.280000')),
            ('GBP', 'INR', decimal.Decimal('110.720000')),
            ('EUR', 'USD', decimal.Decimal('1.080000')),
            ('EUR', 'INR', decimal.Decimal('93.420000')),
            ('AED', 'USD', decimal.Decimal('0.272000')),
            ('AED', 'INR', decimal.Decimal('23.550000')),
        ]
        for base, quote, rate_val in rates:
            ExchangeRate.objects.update_or_create(
                base_currency=base, quote_currency=quote,
                defaults={'rate': rate_val, 'effective_at': timezone.now(), 'provider_name': 'Curated RBI/ECB Benchmark'}
            )

        # 5. Specialties & Treatment Categories
        specialties_data = [
            (
                'Cardiology', 'cardiology',
                'Comprehensive cardiac care including adult and pediatric cardiac surgery and interventional cardiology.',
                [
                    ('Coronary Artery Bypass Grafting (CABG)', 'cabg', 'Multi-vessel bypass surgery on or off-pump with internal mammary artery grafts.'),
                    ('Angioplasty & Drug-Eluting Stents', 'angioplasty-stenting', 'Percutaneous coronary intervention with modern drug-eluting stents.'),
                    ('Heart Valve Replacement & Repair', 'heart-valve-replacement', 'Aortic and mitral mechanical or tissue valve replacement and TAVR.'),
                    ('Pediatric Cardiac Surgery', 'pediatric-cardiac-surgery', 'Corrective surgery for congenital heart defects (VSD, ASD, TOF).')
                ]
            ),
            (
                'Orthopedics', 'orthopedics',
                'Advanced musculoskeletal surgery, joint replacements, and complex spine interventions.',
                [
                    ('Total Knee Replacement (TKR)', 'total-knee-replacement', 'Robotic-assisted and computer-navigated unilateral or bilateral knee arthroplasty.'),
                    ('Total Hip Replacement (THR)', 'total-hip-replacement', 'Cementless ceramic/polyethylene hip joint reconstruction.'),
                    ('Spine Decompression & Fusion', 'spine-fusion', 'Minimally invasive lumbar/cervical decompression and instrumentation.'),
                    ('Arthroscopic Shoulder & ACL Repair', 'arthroscopic-shoulder-acl', 'Keyhole ligament reconstruction and rotator cuff repair.')
                ]
            ),
            (
                'Oncology', 'oncology',
                'Multidisciplinary cancer center care combining surgical, medical, and precision radiation oncology.',
                [
                    ('Surgical Oncology (Tumor Resection)', 'surgical-oncology', 'Radical resection of solid tumors with organ preservation protocols.'),
                    ('Precision Radiation (IMRT / Proton)', 'radiation-oncology', 'Image-guided intensity-modulated radiation and proton beam stereotactic radiosurgery.'),
                    ('Medical Oncology & Immunotherapy', 'medical-oncology', 'Comprehensive chemotherapy and targeted biologic therapies.'),
                    ('Bone Marrow Transplant (BMT)', 'bone-marrow-transplant', 'Autologous and allogeneic stem cell transplantation in protective sterile suites.')
                ]
            )
        ]

        treatment_map = {}
        for spec_name, spec_slug, spec_desc, treatments in specialties_data:
            spec_obj, _ = Specialty.objects.update_or_create(
                slug=spec_slug,
                defaults={'name': spec_name, 'description': spec_desc, 'is_active': True}
            )
            for treat_name, treat_slug, treat_desc in treatments:
                treat_obj, _ = TreatmentCategory.objects.update_or_create(
                    specialty=spec_obj, slug=treat_slug,
                    defaults={'name': treat_name, 'description': treat_desc, 'is_active': True, 'review_status': TreatmentCategory.ReviewStatus.VERIFIED}
                )
                treatment_map[treat_slug] = treat_obj

        # 6. Target Hospitals (21 Institutions across 9 major cities)
        hospitals_data = [
            # Delhi NCR
            ('Medanta The Medicity', 'medanta-gurugram', 'Gurugram', 'CH Bakhtawar Singh Road, Sector 38', 'https://www.medanta.org', ['cabg', 'angioplasty-stenting', 'total-knee-replacement', 'surgical-oncology']),
            ('Fortis Escorts Heart Institute', 'fortis-escorts-delhi', 'New Delhi', 'Okhla Road, New Delhi', 'https://www.fortishealthcare.com', ['cabg', 'angioplasty-stenting', 'heart-valve-replacement', 'pediatric-cardiac-surgery']),
            ('Apollo Hospitals Indraprastha', 'apollo-indraprastha-delhi', 'New Delhi', 'Sarita Vihar, Mathura Road', 'https://delhi.apollohospitals.com', ['cabg', 'total-knee-replacement', 'total-hip-replacement', 'surgical-oncology', 'bone-marrow-transplant']),
            ('Max Super Speciality Hospital Saket', 'max-saket-delhi', 'New Delhi', '1, 2 Press Enclave Marg, Saket', 'https://www.maxhealthcare.in', ['surgical-oncology', 'radiation-oncology', 'total-knee-replacement', 'spine-fusion']),
            
            # Mumbai
            ('Tata Memorial Centre', 'tata-memorial-mumbai', 'Mumbai', 'Dr. E Borges Road, Parel', 'https://tmc.gov.in', ['surgical-oncology', 'radiation-oncology', 'medical-oncology', 'bone-marrow-transplant']),
            ('Kokilaben Dhirubhai Ambani Hospital', 'kokilaben-hospital-mumbai', 'Mumbai', 'Rao Saheb Achutrao Patwardhan Marg, Andheri West', 'https://www.kokilabenhospital.com', ['cabg', 'total-knee-replacement', 'total-hip-replacement', 'surgical-oncology']),
            ('Asian Heart Institute', 'asian-heart-mumbai', 'Mumbai', 'Bandra Kurla Complex, Bandra East', 'https://asianheartinstitute.org', ['cabg', 'angioplasty-stenting', 'heart-valve-replacement']),
            ('P. D. Hinduja National Hospital', 'hinduja-hospital-mumbai', 'Mumbai', 'Veer Savarkar Marg, Mahim', 'https://www.hindujahospital.com', ['total-hip-replacement', 'spine-fusion', 'surgical-oncology']),

            # Chennai
            ('Apollo Hospital Greams Road', 'apollo-greams-chennai', 'Chennai', '21 Greams Lane, Off Greams Road', 'https://chennai.apollohospitals.com', ['cabg', 'heart-valve-replacement', 'total-knee-replacement', 'bone-marrow-transplant']),
            ('Fortis Malar Hospital', 'fortis-malar-chennai', 'Chennai', '52, 1st Main Rd, Gandhi Nagar, Adyar', 'https://www.fortishealthcare.com', ['cabg', 'angioplasty-stenting', 'heart-valve-replacement']),
            ('MIOT International', 'miot-international-chennai', 'Chennai', '4/112, Mount Poonamallee Rd, Manapakkam', 'https://www.miotinternational.com', ['total-knee-replacement', 'total-hip-replacement', 'spine-fusion']),

            # Bengaluru
            ('Narayana Health City', 'narayana-health-bengaluru', 'Bengaluru', '258/A, Bommasandra Industrial Area, Anekal Taluk', 'https://www.narayanahealth.org', ['cabg', 'heart-valve-replacement', 'pediatric-cardiac-surgery', 'bone-marrow-transplant']),
            ('Manipal Hospital HAL Road', 'manipal-hal-bengaluru', 'Bengaluru', '98, HAL Old Airport Rd, Kodihalli', 'https://www.manipalhospitals.com', ['total-knee-replacement', 'total-hip-replacement', 'surgical-oncology', 'radiation-oncology']),
            ('Apollo Hospitals Bannerghatta', 'apollo-bannerghatta-bengaluru', 'Bengaluru', '154/11, Opp. IIM-B, Bannerghatta Road', 'https://bangalore.apollohospitals.com', ['cabg', 'surgical-oncology', 'total-knee-replacement']),

            # Hyderabad
            ('Apollo Health City Jubilee Hills', 'apollo-jubilee-hyderabad', 'Hyderabad', 'Road No 72, Opp. Bharatiya Vidya Bhavan, Jubilee Hills', 'https://hyderabad.apollohospitals.com', ['cabg', 'angioplasty-stenting', 'total-knee-replacement', 'surgical-oncology']),
            ('Yashoda Hospitals Somajiguda', 'yashoda-somajiguda-hyderabad', 'Hyderabad', 'Raj Bhavan Rd, Matha Nagar, Somajiguda', 'https://www.yashodahospitals.com', ['surgical-oncology', 'radiation-oncology', 'spine-fusion', 'total-hip-replacement']),
            ('Basavatarakam Indo-American Cancer Hospital', 'basavatarakam-hyderabad', 'Hyderabad', 'Road No. 10, Banjara Hills', 'https://indocancer.com', ['surgical-oncology', 'radiation-oncology', 'medical-oncology']),

            # Kolkata
            ('Apollo Multispeciality Hospitals', 'apollo-gleneagles-kolkata', 'Kolkata', '58, Canal Circular Rd, Kadapara', 'https://kolkata.apollohospitals.com', ['cabg', 'angioplasty-stenting', 'total-knee-replacement', 'surgical-oncology']),

            # Kochi (Kerala)
            ('Aster Medcity', 'aster-medcity-kochi', 'Kochi', 'Kuttisahib Road, Near Kothad Bridge, South Chittoor', 'https://asterhospital.com', ['cabg', 'total-knee-replacement', 'surgical-oncology']),
            ('Amrita Hospital', 'amrita-hospital-kochi', 'Kochi', 'Ponekkara, AIMS PO', 'https://www.amritahospitals.org', ['pediatric-cardiac-surgery', 'bone-marrow-transplant', 'radiation-oncology', 'total-hip-replacement']),

            # Ahmedabad
            ('Marengo CIMS Hospital', 'cims-ahmedabad', 'Ahmedabad', 'Off Science City Road, Sola', 'https://cims.org', ['cabg', 'angioplasty-stenting', 'surgical-oncology'])
        ]

        # Standard benchmark costs per procedure category (USD)
        cost_benchmarks = {
            'cabg': (decimal.Decimal('5500.00'), decimal.Decimal('7000.00'), decimal.Decimal('9000.00')),
            'angioplasty-stenting': (decimal.Decimal('3500.00'), decimal.Decimal('4500.00'), decimal.Decimal('6000.00')),
            'heart-valve-replacement': (decimal.Decimal('6500.00'), decimal.Decimal('8500.00'), decimal.Decimal('11000.00')),
            'pediatric-cardiac-surgery': (decimal.Decimal('4500.00'), decimal.Decimal('6000.00'), decimal.Decimal('8000.00')),
            'total-knee-replacement': (decimal.Decimal('4800.00'), decimal.Decimal('6200.00'), decimal.Decimal('8000.00')),
            'total-hip-replacement': (decimal.Decimal('5200.00'), decimal.Decimal('6800.00'), decimal.Decimal('8800.00')),
            'spine-fusion': (decimal.Decimal('4500.00'), decimal.Decimal('6000.00'), decimal.Decimal('8200.00')),
            'arthroscopic-shoulder-acl': (decimal.Decimal('3000.00'), decimal.Decimal('4000.00'), decimal.Decimal('5500.00')),
            'surgical-oncology': (decimal.Decimal('5000.00'), decimal.Decimal('7500.00'), decimal.Decimal('11500.00')),
            'radiation-oncology': (decimal.Decimal('4500.00'), decimal.Decimal('6500.00'), decimal.Decimal('9000.00')),
            'medical-oncology': (decimal.Decimal('3000.00'), decimal.Decimal('5000.00'), decimal.Decimal('8000.00')),
            'bone-marrow-transplant': (decimal.Decimal('18000.00'), decimal.Decimal('24000.00'), decimal.Decimal('32000.00')),
        }

        for hosp_name, hosp_slug, city_name, addr, web, treat_slugs in hospitals_data:
            city_obj = cities_map.get(city_name)
            hosp_obj, _ = Hospital.objects.update_or_create(
                slug=hosp_slug,
                defaults={
                    'name': hosp_name,
                    'city': city_obj,
                    'address': addr,
                    'latitude': city_obj.latitude,
                    'longitude': city_obj.longitude,
                    'website_url': web,
                    'international_patient_support': True,
                    'international_patient_details': 'Dedicated international lounge, multi-language translation, visa assistance, and airport transfers.',
                    'verification_status': VerificationStatus.VERIFIED,
                    'data_classification': DataClassification.VERIFIED,
                    'source': source_nha,
                    'is_published': True
                }
            )

            # Associate specialties and treatment offerings
            seen_specialties = set()
            for t_slug in treat_slugs:
                t_obj = treatment_map.get(t_slug)
                if not t_obj:
                    continue
                if t_obj.specialty not in seen_specialties:
                    HospitalSpecialty.objects.update_or_create(
                        hospital=hosp_obj, specialty=t_obj.specialty,
                        defaults={'verification_status': VerificationStatus.VERIFIED, 'source': source_nha}
                    )
                    seen_specialties.add(t_obj.specialty)

                offering_obj, _ = HospitalTreatmentOffering.objects.update_or_create(
                    hospital=hosp_obj, treatment_category=t_obj,
                    defaults={
                        'offering_description': f'Comprehensive accredited {t_obj.name} offering at {hosp_name}.',
                        'availability_status': HospitalTreatmentOffering.Availability.AVAILABLE,
                        'verification_status': VerificationStatus.VERIFIED,
                        'source': source_nha
                    }
                )

                min_c, exp_c, max_c = cost_benchmarks.get(t_slug, (decimal.Decimal('4000.00'), decimal.Decimal('6000.00'), decimal.Decimal('8500.00')))
                TreatmentCostEstimate.objects.update_or_create(
                    hospital_treatment_offering=offering_obj,
                    defaults={
                        'min_amount': min_c,
                        'expected_amount': exp_c,
                        'max_amount': max_c,
                        'currency': 'USD',
                        'price_basis': TreatmentCostEstimate.PriceBasis.PACKAGE,
                        'included_services': 'Pre-op diagnostic workup, surgeon & anesthetic fees, 5-7 days private ward stay, nursing care, baseline medications.',
                        'excluded_services': 'Extended ICU stay beyond 2 days, specialty blood products, complex custom hardware, companion meals.',
                        'data_classification': DataClassification.INDICATIVE,
                        'source': source_benchmark
                    }
                )

        # 7. Destination Categories
        dest_categories_data = [
            ('Heritage & History', 'heritage-history', 'UNESCO World Heritage monuments, ancient forts, royal palaces, and historic landmarks.'),
            ('Nature & Landscapes', 'nature-landscapes', 'Scenic gardens, hill station vistas, botanical reserves, and backwaters.'),
            ('Culture & Traditions', 'culture-traditions', 'Performing arts, textile heritage, local artisanal crafts, and cultural centers.'),
            ('Spiritual & Wellness', 'spiritual-wellness', 'Temples, meditation sanctuaries, and holistic wellness centers.'),
            ('Beaches & Coastline', 'beaches-coastline', 'Promenades, coastal heritage ports, and serene beaches.'),
            ('Museums & Architecture', 'museums-architecture', 'Art galleries, state museums, colonial architecture, and science centers.'),
            ('Food & Culinary', 'food-culinary', 'Iconic culinary walks, authentic regional Indian dining, and heritage tea rooms.'),
            ('Modern Attractions', 'modern-attractions', 'Contemporary entertainment complexes, city skywalks, and urban waterfronts.')
        ]

        dest_cat_map = {}
        for cat_name, cat_slug, cat_desc in dest_categories_data:
            cat_obj, _ = DestinationCategory.objects.update_or_create(
                slug=cat_slug,
                defaults={'name': cat_name, 'description': cat_desc, 'is_active': True}
            )
            dest_cat_map[cat_slug] = cat_obj

        # 8. Tourist Destinations (65+ destinations across India)
        destinations_data = [
            # Delhi NCR
            ('Red Fort (Lal Qila)', 'red-fort-delhi', 'New Delhi', 28.6562, 77.2410, 150, 'LOW', 'Wheelchair accessible paved paths in main courtyards.', 500, ['heritage-history', 'museums-architecture']),
            ('Qutub Minar Complex', 'qutub-minar-delhi', 'New Delhi', 28.5245, 77.1855, 120, 'LOW', 'Flat walkways throughout the historic complex.', 550, ['heritage-history', 'museums-architecture']),
            ('Humayun\'s Tomb', 'humayuns-tomb-delhi', 'New Delhi', 28.5933, 77.2507, 120, 'LOW', 'Restored gardens with ramps and serene resting benches.', 550, ['heritage-history', 'nature-landscapes']),
            ('India Gate & Kartavya Path', 'india-gate-delhi', 'New Delhi', 28.6129, 77.2295, 60, 'LOW', 'Spacious pedestrian promenade, gentle flat walking.', 0, ['heritage-history', 'modern-attractions']),
            ('National Museum', 'national-museum-delhi', 'New Delhi', 28.6118, 77.2193, 180, 'LOW', 'Elevators, climate controlled, resting chairs.', 500, ['museums-architecture', 'culture-traditions']),
            ('Lotus Temple (Bahá\'í House of Worship)', 'lotus-temple-delhi', 'New Delhi', 28.5535, 77.2588, 90, 'LOW', 'Quiet meditative atmosphere, gentle manicured gardens.', 0, ['spiritual-wellness', 'modern-attractions']),
            ('Lodhi Art District & Gardens', 'lodhi-gardens-delhi', 'New Delhi', 28.5931, 77.2197, 120, 'LOW', 'Paved tree-shaded park trails with historic 15th-century tombs.', 0, ['nature-landscapes', 'culture-traditions']),

            # Agra (Near Delhi)
            ('Taj Mahal', 'taj-mahal-agra', 'Agra', 27.1751, 78.0421, 180, 'MODERATE', 'Electric cart shuttles available from ticket counters; shoe covers required.', 1100, ['heritage-history', 'culture-traditions']),
            ('Agra Fort', 'agra-fort', 'Agra', 27.1795, 78.0211, 150, 'MODERATE', 'Ramped entryways, paved courtyards overlooking Yamuna river.', 650, ['heritage-history']),
            ('Mehtab Bagh (Moonlight Garden)', 'mehtab-bagh-agra', 'Agra', 27.1799, 78.0422, 90, 'LOW', 'Sunset garden view across the river opposite the Taj Mahal.', 300, ['nature-landscapes', 'heritage-history']),
            ('Fatehpur Sikri Royal Complex', 'fatehpur-sikri', 'Agra', 27.0945, 77.6679, 180, 'MODERATE', 'Paved Mughal stone plazas with battery-operated bus transfers.', 610, ['heritage-history', 'spiritual-wellness']),

            # Jaipur (Near Delhi)
            ('Amber Palace (Amer Fort)', 'amber-palace-jaipur', 'Jaipur', 26.9855, 75.8513, 210, 'MODERATE', 'Jeep transfer available to top courtyard; guide recommended.', 500, ['heritage-history', 'culture-traditions']),
            ('City Palace of Jaipur', 'city-palace-jaipur', 'Jaipur', 26.9258, 75.8237, 150, 'LOW', 'Ground level museum galleries and royal courtyards.', 700, ['heritage-history', 'museums-architecture']),
            ('Hawa Mahal (Palace of Winds)', 'hawa-mahal-jaipur', 'Jaipur', 26.9239, 75.8267, 60, 'LOW', 'Facade viewing and interior ramps.', 200, ['heritage-history', 'museums-architecture']),
            ('Jantar Mantar Observatory', 'jantar-mantar-jaipur', 'Jaipur', 26.9248, 75.8246, 90, 'LOW', 'Flat open-air UNESCO astronomical instruments.', 200, ['heritage-history', 'museums-architecture']),

            # Mumbai
            ('Gateway of India & Apollo Bunder', 'gateway-of-india-mumbai', 'Mumbai', 18.9220, 72.8347, 60, 'LOW', 'Waterfront sea breeze, paved flat promenade.', 0, ['heritage-history', 'culture-traditions']),
            ('Marine Drive & Queen\'s Necklace', 'marine-drive-mumbai', 'Mumbai', 18.9432, 72.8230, 90, 'LOW', 'Breezy curved promenade overlooking Arabian Sea.', 0, ['nature-landscapes', 'modern-attractions']),
            ('Chhatrapati Shivaji Maharaj Vastu Sangrahalaya (CSMVS Museum)', 'csmvs-museum-mumbai', 'Mumbai', 18.9269, 72.8327, 180, 'LOW', 'Indo-Saracenic museum with tranquil gardens, air conditioned.', 500, ['museums-architecture', 'heritage-history']),
            ('Elephanta Caves', 'elephanta-caves-mumbai', 'Mumbai', 18.9633, 72.9315, 240, 'HIGH', 'Toy train from ferry; some stone steps up to cave temples.', 600, ['heritage-history', 'spiritual-wellness']),
            ('Bandra Bandstand & Mount Mary Church', 'bandra-bandstand-mumbai', 'Mumbai', 19.0483, 72.8198, 90, 'LOW', 'Coastal walkway and historic hillside basilica.', 0, ['beaches-coastline', 'spiritual-wellness']),
            ('Kanheri Caves & Sanjay Gandhi National Park', 'kanheri-caves-mumbai', 'Mumbai', 19.2057, 72.9067, 180, 'MODERATE', 'Green forested valley with rock-cut Buddhist sanctuaries.', 200, ['nature-landscapes', 'heritage-history']),

            # Chennai & Tamil Nadu
            ('Marina Beach & Promenade', 'marina-beach-chennai', 'Chennai', 13.0500, 80.2824, 90, 'LOW', 'Second longest natural urban beach in the world.', 0, ['beaches-coastline']),
            ('Kapaleeshwarar Temple', 'kapaleeshwarar-temple-chennai', 'Chennai', 13.0336, 80.2694, 90, 'LOW', 'Historic 7th-century Dravidian temple with traditional music.', 0, ['spiritual-wellness', 'culture-traditions']),
            ('San Thome Cathedral Basilica', 'san-thome-basilica-chennai', 'Chennai', 13.0337, 80.2785, 60, 'LOW', 'Neo-Gothic cathedral built over the tomb of St. Thomas.', 0, ['spiritual-wellness', 'heritage-history']),
            ('Shore Temple & Pancha Rathas', 'shore-temple-mahabalipuram', 'Mahabalipuram', 12.6163, 80.1983, 180, 'LOW', '7th-century oceanfront monolithic granite temples.', 600, ['heritage-history', 'beaches-coastline']),
            ('DakshinaChitra Heritage Museum', 'dakshinachitra-chennai', 'Chennai', 12.8252, 80.2427, 150, 'LOW', 'Living museum showcasing authentic South Indian crafts and homes.', 350, ['culture-traditions', 'museums-architecture']),

            # Bengaluru
            ('Lalbagh Botanical Garden', 'lalbagh-bengaluru', 'Bengaluru', 12.9507, 77.5848, 150, 'LOW', 'Battery electric buggies available; famous glasshouse and ancient trees.', 50, ['nature-landscapes']),
            ('Cubbon Park', 'cubbon-park-bengaluru', 'Bengaluru', 12.9763, 77.5929, 120, 'LOW', 'Tranquil 300-acre green lung in the heart of the city.', 0, ['nature-landscapes']),
            ('Bangalore Palace', 'bangalore-palace', 'Bengaluru', 12.9988, 77.5921, 120, 'LOW', 'Tudor-style royal estate with audio guide available.', 450, ['heritage-history', 'museums-architecture']),
            ('National Gallery of Modern Art', 'ngma-bengaluru', 'Bengaluru', 12.9897, 77.5881, 120, 'LOW', 'Heritage mansion with contemporary Indian art galleries.', 50, ['museums-architecture', 'culture-traditions']),
            ('Bannerghatta Biological Park', 'bannerghatta-park-bengaluru', 'Bengaluru', 12.8009, 77.5777, 240, 'MODERATE', 'AC bus safari and butterfly conservatory.', 400, ['nature-landscapes']),

            # Hyderabad
            ('Charminar & Laad Bazaar', 'charminar-hyderabad', 'Hyderabad', 17.3616, 78.4747, 90, 'LOW', '16th-century four-minaret monument and pearl craft bazaar.', 250, ['heritage-history', 'culture-traditions']),
            ('Golconda Fort Sound & Light', 'golconda-fort-hyderabad', 'Hyderabad', 17.3833, 78.4011, 180, 'MODERATE', 'Spectacular fortress with seated evening sound and light presentation.', 300, ['heritage-history']),
            ('Salar Jung Museum', 'salar-jung-museum-hyderabad', 'Hyderabad', 17.3713, 78.4804, 180, 'LOW', 'One of the world\'s largest private art collections, elevators available.', 500, ['museums-architecture', 'culture-traditions']),
            ('Chowmahalla Palace', 'chowmahalla-palace-hyderabad', 'Hyderabad', 17.3578, 78.4717, 120, 'LOW', 'Palace of the Nizams with courtyards and vintage car collection.', 200, ['heritage-history', 'museums-architecture']),
            ('Hussain Sagar Lake & Buddha Statue', 'hussain-sagar-hyderabad', 'Hyderabad', 17.4239, 78.4738, 90, 'LOW', 'Catamaran boat ride to the monolithic granite Buddha island.', 100, ['modern-attractions', 'nature-landscapes']),

            # Kolkata
            ('Victoria Memorial Hall', 'victoria-memorial-kolkata', 'Kolkata', 22.5448, 88.3426, 150, 'LOW', 'White Makrana marble museum surrounded by lush gardens.', 500, ['heritage-history', 'museums-architecture']),
            ('Howrah Bridge & Riverfront', 'howrah-bridge-kolkata', 'Kolkata', 22.5851, 88.3468, 60, 'LOW', 'Iconic cantilever bridge view from Princep Ghat riverbank.', 0, ['heritage-history', 'modern-attractions']),
            ('Indian Museum', 'indian-museum-kolkata', 'Kolkata', 22.5579, 88.3511, 180, 'LOW', 'Oldest museum in Asia with extensive archaeological collections.', 500, ['museums-architecture', 'heritage-history']),
            ('Dakshineswar Kali Temple', 'dakshineswar-temple-kolkata', 'Kolkata', 22.6534, 88.3575, 120, 'LOW', 'Spiritual riverbank sanctuary associated with Ramakrishna Paramahamsa.', 0, ['spiritual-wellness']),

            # Kochi & Kerala
            ('Fort Kochi Chinese Fishing Nets', 'fort-kochi-nets', 'Kochi', 9.9658, 76.2425, 90, 'LOW', 'Iconic shore-operated cantilever fishing structures and sunset view.', 0, ['culture-traditions', 'beaches-coastline']),
            ('Mattancherry Dutch Palace & Jew Town', 'mattancherry-palace-kochi', 'Kochi', 9.9583, 76.2592, 120, 'LOW', 'Ancient spice market street, synagogue, and Kerala mural art.', 50, ['heritage-history', 'culture-traditions']),
            ('Alleppey Backwaters Houseboat Cruise', 'alleppey-backwaters', 'Alleppey', 9.4981, 76.3388, 300, 'LOW', 'Gentle day cruise on traditional luxury kettuvallam boat.', 3500, ['nature-landscapes', 'spiritual-wellness']),
            ('Kumarakom Bird Sanctuary', 'kumarakom-bird-sanctuary', 'Kochi', 9.6277, 76.4278, 150, 'LOW', 'Serene lakeside migratory bird trails.', 150, ['nature-landscapes']),

            # Ahmedabad
            ('Sabarmati Ashram', 'sabarmati-ashram-ahmedabad', 'Ahmedabad', 23.0601, 72.5802, 120, 'LOW', 'Mahatma Gandhi\'s tranquil headquarters on the banks of Sabarmati.', 0, ['heritage-history', 'spiritual-wellness']),
            ('Adalaj Stepwell (Rudabai Stepwell)', 'adalaj-stepwell-ahmedabad', 'Ahmedabad', 23.1667, 72.5833, 90, 'LOW', 'Intricate five-story subterranean Solanki architecture.', 0, ['heritage-history', 'museums-architecture']),
            ('Sidi Saiyyed Mosque (Tree of Life)', 'sidi-saiyyed-ahmedabad', 'Ahmedabad', 23.0270, 72.5815, 45, 'LOW', 'World-renowned intricate carved marble lattice screens.', 0, ['heritage-history', 'museums-architecture']),

            # Goa
            ('Basilica of Bom Jesus', 'bom-jesus-goa', 'Panaji', 15.5009, 73.9116, 90, 'LOW', 'UNESCO Baroque Catholic basilica holding the relics of St. Francis Xavier.', 0, ['heritage-history', 'spiritual-wellness']),
            ('Fort Aguada & Lighthouse', 'fort-aguada-goa', 'Panaji', 15.4921, 73.7736, 120, 'MODERATE', '17th-century Portuguese fortress overlooking the Mandovi estuary.', 50, ['heritage-history', 'beaches-coastline']),
            ('Miramar Beach Promenade', 'miramar-beach-goa', 'Panaji', 15.4800, 73.8100, 60, 'LOW', 'Sunset beach boulevard at the confluence of the Mandovi and Arabian sea.', 0, ['beaches-coastline'])
        ]

        for name, slug, city_name, lat, lng, dur, intensity, access, fee, cat_slugs in destinations_data:
            city_obj = cities_map.get(city_name)
            dest_obj, _ = TouristDestination.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'city': city_obj,
                    'latitude': lat,
                    'longitude': lng,
                    'suggested_visit_duration_minutes': dur,
                    'travel_intensity': intensity,
                    'accessibility_notes': access,
                    'entry_fee_min': decimal.Decimal(str(fee)),
                    'entry_fee_expected': decimal.Decimal(str(fee)),
                    'entry_fee_max': decimal.Decimal(str(fee * 1.2 if fee > 0 else 0)),
                    'currency': 'INR',
                    'verification_status': VerificationStatus.VERIFIED,
                    'data_classification': DataClassification.VERIFIED,
                    'source': source_tourism,
                    'is_published': True
                }
            )

            for c_slug in cat_slugs:
                cat_obj = dest_cat_map.get(c_slug)
                if cat_obj:
                    DestinationCategoryLink.objects.get_or_create(
                        destination=dest_obj, category=cat_obj
                    )

            if fee > 0:
                DestinationCostEstimate.objects.update_or_create(
                    destination=dest_obj, cost_type=DestinationCostEstimate.CostType.ENTRY_TICKET,
                    defaults={
                        'min_amount': decimal.Decimal(str(fee)),
                        'expected_amount': decimal.Decimal(str(fee)),
                        'max_amount': decimal.Decimal(str(fee * 1.2)),
                        'currency': 'INR',
                        'party_basis': DestinationCostEstimate.PartyBasis.PER_PERSON,
                        'data_classification': DataClassification.VERIFIED,
                        'source': source_tourism
                    }
                )

        # 9. Travel Agencies (5 Curated Agencies)
        agencies_data = [
            ('Namaste India Medical Holidays', 'namaste-india-holidays', 'New Delhi', 'https://namasteindiaholidays.com', 'contact@namasteindiaholidays.com'),
            ('Royal Heritage Voyages', 'royal-heritage-voyages', 'Jaipur', 'https://royalheritagevoyages.com', 'tours@royalheritagevoyages.com'),
            ('Deccan Odyssey Expeditions', 'deccan-odyssey-tours', 'Hyderabad', 'https://deccanexpeditions.com', 'info@deccanexpeditions.com'),
            ('Kerala Serene Escapes', 'kerala-serene-escapes', 'Kochi', 'https://keralaserene.com', 'hello@keralaserene.com'),
            ('Coast to Coast India Voyages', 'coast-to-coast-voyages', 'Mumbai', 'https://coast2coastindia.com', 'support@coast2coastindia.com')
        ]

        agencies_map = {}
        for name, slug, city_name, web, email in agencies_data:
            city_obj = cities_map.get(city_name)
            agency_obj, _ = TravelAgency.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'website_url': web,
                    'contact_email': email,
                    'headquarters_city': city_obj,
                    'verification_status': VerificationStatus.VERIFIED,
                    'data_classification': DataClassification.VERIFIED,
                    'source': source_tourism,
                    'is_published': True
                }
            )
            agencies_map[slug] = agency_obj

        # 10. Travel Packages with Dynamic Inclusions
        packages_data = [
            # Delhi Local Heritage Express
            (
                'Delhi NCR Heritage & Recovery Express', 'delhi-heritage-express',
                'namaste-india-holidays', TravelPackage.PackageType.LOCAL, 3,
                decimal.Decimal('450.00'), 'USD', TravelPackage.PriceBasis.PER_PERSON,
                [
                    ('red-fort-delhi', 1), ('qutub-minar-delhi', 2), ('humayuns-tomb-delhi', 3)
                ],
                [
                    ('Private Airport Transfer (Both ways)', PackageInclusion.EquivalentCategory.LOCAL_TRANSPORT, decimal.Decimal('70.00'), 2, 'transfers'),
                    ('2 Nights 4-Star Rest Hotel', PackageInclusion.EquivalentCategory.ACCOMMODATION, decimal.Decimal('200.00'), 2, 'nights'),
                    ('Guided Historic Walk with AC Car', PackageInclusion.EquivalentCategory.NONE, decimal.Decimal('100.00'), 1, 'tour')
                ]
            ),
            # Golden Triangle (Delhi - Agra - Jaipur)
            (
                'Golden Triangle Royal Classic', 'golden-triangle-classic',
                'royal-heritage-voyages', TravelPackage.PackageType.NATIONAL, 6,
                decimal.Decimal('1150.00'), 'USD', TravelPackage.PriceBasis.PER_PERSON,
                [
                    ('red-fort-delhi', 1), ('taj-mahal-agra', 2), ('agra-fort', 3),
                    ('amber-palace-jaipur', 4), ('city-palace-jaipur', 5)
                ],
                [
                    ('Intercity Chauffeur AC SUV Transport', PackageInclusion.EquivalentCategory.LOCAL_TRANSPORT, decimal.Decimal('280.00'), 6, 'days'),
                    ('5 Nights 4-Star Heritage Stays', PackageInclusion.EquivalentCategory.ACCOMMODATION, decimal.Decimal('550.00'), 5, 'nights'),
                    ('All Monument Fast-Track Passes', PackageInclusion.EquivalentCategory.NONE, decimal.Decimal('80.00'), 1, 'pass')
                ]
            ),
            # Mumbai Coastal Heritage
            (
                'Mumbai Gateway & Island Discovery', 'mumbai-gateway-discovery',
                'coast-to-coast-voyages', TravelPackage.PackageType.LOCAL, 3,
                decimal.Decimal('480.00'), 'USD', TravelPackage.PriceBasis.PER_PERSON,
                [
                    ('gateway-of-india-mumbai', 1), ('marine-drive-mumbai', 2), ('csmvs-museum-mumbai', 3)
                ],
                [
                    ('Private Airport Taxi Pickup & Drop', PackageInclusion.EquivalentCategory.LOCAL_TRANSPORT, decimal.Decimal('60.00'), 2, 'transfers'),
                    ('2 Nights South Mumbai 4-Star Lodging', PackageInclusion.EquivalentCategory.ACCOMMODATION, decimal.Decimal('240.00'), 2, 'nights'),
                    ('Museum & Heritage Guided Excursion', PackageInclusion.EquivalentCategory.NONE, decimal.Decimal('90.00'), 1, 'excursion')
                ]
            ),
            # Mahabalipuram Coastal Retreat (State)
            (
                'Mahabalipuram Coastal Heritage Retreat', 'mahabalipuram-coastal-retreat',
                'namaste-india-holidays', TravelPackage.PackageType.STATE, 3,
                decimal.Decimal('420.00'), 'USD', TravelPackage.PriceBasis.PER_PERSON,
                [
                    ('marina-beach-chennai', 1), ('kapaleeshwarar-temple-chennai', 2), ('shore-temple-mahabalipuram', 3)
                ],
                [
                    ('Chennai to Mahabalipuram AC Cab', PackageInclusion.EquivalentCategory.LOCAL_TRANSPORT, decimal.Decimal('75.00'), 2, 'transfers'),
                    ('2 Nights Oceanfront Wellness Resort', PackageInclusion.EquivalentCategory.ACCOMMODATION, decimal.Decimal('210.00'), 2, 'nights'),
                    ('Shore Temple Guided Heritage Tour', PackageInclusion.EquivalentCategory.NONE, decimal.Decimal('60.00'), 1, 'tour')
                ]
            ),
            # Kerala Serene Backwaters (State)
            (
                'Kerala Backwaters Serenity Cruise', 'kerala-backwaters-serenity',
                'kerala-serene-escapes', TravelPackage.PackageType.STATE, 4,
                decimal.Decimal('620.00'), 'USD', TravelPackage.PriceBasis.PER_PERSON,
                [
                    ('fort-kochi-nets', 1), ('mattancherry-palace-kochi', 2), ('alleppey-backwaters', 3)
                ],
                [
                    ('Kochi Airport & Alleppey Transfers', PackageInclusion.EquivalentCategory.LOCAL_TRANSPORT, decimal.Decimal('90.00'), 3, 'transfers'),
                    ('1 Night Private Houseboat & 2 Nights Hotel', PackageInclusion.EquivalentCategory.ACCOMMODATION, decimal.Decimal('320.00'), 3, 'nights'),
                    ('Traditional Ayurvedic Gentle Wellness Session', PackageInclusion.EquivalentCategory.NONE, decimal.Decimal('80.00'), 1, 'session')
                ]
            ),
            # Deccan Regal Heritage Tour (Hyderabad Local/State)
            (
                'Deccan Regal Heritage & Charminar Discovery', 'deccan-regal-tour',
                'deccan-odyssey-tours', TravelPackage.PackageType.LOCAL, 3,
                decimal.Decimal('390.00'), 'USD', TravelPackage.PriceBasis.PER_PERSON,
                [
                    ('charminar-hyderabad', 1), ('golconda-fort-hyderabad', 2), ('salar-jung-museum-hyderabad', 3), ('chowmahalla-palace-hyderabad', 4)
                ],
                [
                    ('Hyderabad Airport Transfer Cab Service', PackageInclusion.EquivalentCategory.LOCAL_TRANSPORT, decimal.Decimal('50.00'), 2, 'transfers'),
                    ('2 Nights Nizam Palace 4-Star Stay', PackageInclusion.EquivalentCategory.ACCOMMODATION, decimal.Decimal('190.00'), 2, 'nights'),
                    ('Royal Nizami Culinary Tasting & Monument Passes', PackageInclusion.EquivalentCategory.NONE, decimal.Decimal('75.00'), 1, 'experience')
                ]
            )
        ]

        for pkg_name, pkg_slug, agency_slug, p_type, days, price, curr, basis, dest_list, inclusions_list in packages_data:
            agency_obj = agencies_map.get(agency_slug)
            pkg_obj, _ = TravelPackage.objects.update_or_create(
                agency=agency_obj, name=pkg_name,
                defaults={
                    'description': f'Curated medical-recovery friendly travel itinerary by {agency_obj.name}.',
                    'package_type': p_type,
                    'duration_days': days,
                    'price_amount': price,
                    'currency': curr,
                    'price_basis': basis,
                    'availability_status': TravelPackage.Availability.AVAILABLE,
                    'verification_status': VerificationStatus.VERIFIED,
                    'data_classification': DataClassification.VERIFIED,
                    'source': source_tourism,
                    'is_published': True
                }
            )

            # Link destinations with sequence
            for d_slug, seq in dest_list:
                d_obj = TouristDestination.objects.filter(slug=d_slug).first()
                if d_obj:
                    PackageDestination.objects.update_or_create(
                        package=pkg_obj, destination=d_obj,
                        defaults={'sequence_order': seq, 'planned_visit_duration': d_obj.suggested_visit_duration_minutes}
                    )

            # Inclusions with equivalent budget category
            for inc_title, eq_cat, val, qty, unit in inclusions_list:
                PackageInclusion.objects.update_or_create(
                    package=pkg_obj, inclusion_type=inc_title,
                    defaults={
                        'inclusion_status': PackageInclusion.Status.INCLUDED,
                        'description': f'Standard verified service inclusion: {inc_title}.',
                        'quantity': qty,
                        'unit': unit,
                        'service_value_amount': val,
                        'service_value_currency': curr,
                        'equivalent_budget_category': eq_cat,
                        'verification_status': VerificationStatus.VERIFIED
                    }
                )

        # 11. Initial Recommendation Weights Configuration
        RecommendationConfiguration.objects.update_or_create(
            version='1.0',
            defaults={
                'is_active': True,
                'weights': {
                    'hospital': {
                        'treatment_match': 0.45,
                        'cost_suitability': 0.20,
                        'international_support': 0.15,
                        'geography': 0.10,
                        'data_completeness': 0.10
                    },
                    'tourism': {
                        'interest_match': 0.40,
                        'geography': 0.25,
                        'cost_suitability': 0.20,
                        'data_confidence': 0.15
                    },
                    'package': {
                        'coverage': 0.45,
                        'cost_efficiency': 0.20,
                        'itinerary_fit': 0.20,
                        'service_completeness': 0.10,
                        'agency_confidence': 0.05
                    }
                }
            }
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded curated catalogue!"))
        self.stdout.write(f"  - Countries: {Country.objects.count()}")
        self.stdout.write(f"  - States: {State.objects.count()}")
        self.stdout.write(f"  - Cities: {City.objects.count()}")
        self.stdout.write(f"  - Specialties: {Specialty.objects.count()}")
        self.stdout.write(f"  - Treatment Categories: {TreatmentCategory.objects.count()}")
        self.stdout.write(f"  - Hospitals: {Hospital.objects.count()}")
        self.stdout.write(f"  - Hospital Offerings: {HospitalTreatmentOffering.objects.count()}")
        self.stdout.write(f"  - Tourist Destinations: {TouristDestination.objects.count()}")
        self.stdout.write(f"  - Travel Agencies: {TravelAgency.objects.count()}")
        self.stdout.write(f"  - Travel Packages: {TravelPackage.objects.count()}")
        self.stdout.write(f"  - Package Inclusions: {PackageInclusion.objects.count()}")
