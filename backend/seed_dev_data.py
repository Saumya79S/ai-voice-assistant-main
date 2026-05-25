"""
Seed development database with sample appointments and agents
Run with: python seed_dev_data.py
"""
import sys
from datetime import date, time, datetime, timedelta
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal
from models.appointment import Appointment, AppointmentStatus
from models.agent import Agent
from models.availability import AvailabilityRule


def seed_appointments():
    """Add sample appointments to the database"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing = db.query(Appointment).count()
        if existing > 0:
            print(f"✓ Database already has {existing} appointments. Skipping seed.")
            return
        
        # Sample appointments
        appointments = [
            Appointment(
                name="John Smith",
                phone="+1-555-0101",
                date=date.today() + timedelta(days=1),
                start_time=time(9, 0),
                end_time=time(9, 30),
                status=AppointmentStatus.confirmed,
                notes="Initial consultation"
            ),
            Appointment(
                name="Sarah Johnson",
                phone="+1-555-0102",
                date=date.today() + timedelta(days=2),
                start_time=time(10, 0),
                end_time=time(10, 30),
                status=AppointmentStatus.confirmed,
                notes="Follow-up meeting"
            ),
            Appointment(
                name="Michael Chen",
                phone="+1-555-0103",
                date=date.today() + timedelta(days=3),
                start_time=time(2, 0, 0),  # 2:00 PM
                end_time=time(2, 30),
                status=AppointmentStatus.confirmed,
                notes="Demo presentation"
            ),
            Appointment(
                name="Emily Davis",
                phone="+1-555-0104",
                date=date.today() + timedelta(days=4),
                start_time=time(14, 0),
                end_time=time(14, 30),
                status=AppointmentStatus.pending,
                notes="Pending confirmation"
            ),
            Appointment(
                name="Robert Wilson",
                phone="+1-555-0105",
                date=date.today() + timedelta(days=5),
                start_time=time(11, 0),
                end_time=time(11, 30),
                status=AppointmentStatus.confirmed,
                notes="Support request"
            ),
            Appointment(
                name="Lisa Anderson",
                phone="+1-555-0106",
                date=date.today() + timedelta(days=6),
                start_time=time(3, 0, 0),  # 3:00 PM
                end_time=time(3, 30),
                status=AppointmentStatus.confirmed,
                notes="Strategy session"
            ),
        ]
        
        db.add_all(appointments)
        db.commit()
        print(f"✓ Added {len(appointments)} sample appointments")
        
    except Exception as e:
        print(f"✗ Error seeding appointments: {e}")
        db.rollback()
    finally:
        db.close()


def seed_agents():
    """Add sample agents to the database"""
    db = SessionLocal()
    
    try:
        # Check if agents already exist
        existing = db.query(Agent).count()
        if existing > 0:
            print(f"✓ Database already has {existing} agents. Skipping seed.")
            return
        
        agents = [
            Agent(
                name="Alex",
                prompt="""You are Alex, a professional AI receptionist for Sky AI Technologies.
Your responsibilities:
- Greet callers warmly and professionally
- Understand their needs and route them appropriately
- Help book appointments during available slots
- Provide information about our services
- Handle appointment inquiries and cancellations

Always be courteous, clear, and efficient. Confirm details before booking appointments.""",
                voice="nova",
                is_active=True
            ),
            Agent(
                name="Jordan",
                prompt="""You are Jordan, a friendly appointment booking specialist for Sky AI Technologies.
Your role:
- Help clients schedule appointments
- Check real-time availability
- Collect necessary information
- Confirm bookings with details
- Answer scheduling questions

Be helpful and ensure all appointment details are correct.""",
                voice="shimmer",
                is_active=True
            ),
        ]
        
        db.add_all(agents)
        db.commit()
        print(f"✓ Added {len(agents)} sample agents")
        
    except Exception as e:
        print(f"✗ Error seeding agents: {e}")
        db.rollback()
    finally:
        db.close()


def seed_availability_rules():
    """Add business hours availability rules"""
    db = SessionLocal()
    
    try:
        # Check if rules already exist
        existing = db.query(AvailabilityRule).count()
        if existing > 0:
            print(f"✓ Database already has {existing} availability rules. Skipping seed.")
            return
        
        # Business hours: 9 AM to 6 PM, Monday to Friday
        # 0 = Monday, 4 = Friday, 5 = Saturday, 6 = Sunday
        rules = []
        
        # Monday to Friday: 9:00 AM - 6:00 PM
        for day in range(0, 5):  # 0-4 = Mon-Fri
            day_name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"][day]
            rules.append(
                AvailabilityRule(
                    day_of_week=day,
                    start_time=time(9, 0),      # 9:00 AM
                    end_time=time(18, 0),       # 6:00 PM
                    slot_duration=30,            # 30-minute slots
                    is_active=True
                )
            )
        
        # Saturday: 10:00 AM - 2:00 PM
        rules.append(
            AvailabilityRule(
                day_of_week=5,                   # Saturday
                start_time=time(10, 0),
                end_time=time(14, 0),
                slot_duration=30,
                is_active=True
            )
        )
        
        # Sunday: Closed (optional - uncomment if you want to explicitly set it as closed)
        # rules.append(
        #     AvailabilityRule(
        #         day_of_week=6,
        #         start_time=time(0, 0),
        #         end_time=time(1, 0),
        #         slot_duration=30,
        #         is_active=False
        #     )
        # )
        
        db.add_all(rules)
        db.commit()
        print(f"✓ Added {len(rules)} availability rules:")
        print("  • Mon-Fri: 9:00 AM - 6:00 PM (30-min slots)")
        print("  • Saturday: 10:00 AM - 2:00 PM (30-min slots)")
        
    except Exception as e:
        print(f"✗ Error seeding availability rules: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding development database...\n")
    seed_appointments()
    seed_agents()
    seed_availability_rules()
    print("\n✅ Database seeding complete!")
