#!/usr/bin/env python3
"""
ARLI Skills Marketplace
Monetization system for custom agent skills

Features:
- Skill package format with metadata
- Marketplace listing and discovery
- Purchase and installation system
- Revenue sharing (90% creator, 10% platform)
- Skill versioning and updates
"""

import json
import hashlib
import tarfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import shutil


class SkillCategory(Enum):
    """Skill categories"""
    CODING = "coding"
    DATA_ANALYSIS = "data_analysis"
    WEB_SCRAPING = "web_scraping"
    AUTOMATION = "automation"
    INTEGRATION = "integration"
    CONTENT = "content"
    SECURITY = "security"
    DEVOPS = "devops"
    OTHER = "other"


class SkillStatus(Enum):
    """Skill status in marketplace"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    REMOVED = "removed"


@dataclass
class SkillMetadata:
    """Skill package metadata"""
    skill_id: str
    name: str
    version: str
    description: str
    category: SkillCategory
    author: str
    author_id: str
    price: float  # in USD
    currency: str = "USD"
    
    # Technical info
    entry_point: str = "skill.py"  # Main file
    dependencies: List[str] = None
    min_arli_version: str = "1.0.0"
    
    # Stats
    downloads: int = 0
    rating: float = 0.0
    review_count: int = 0
    
    # Status
    status: SkillStatus = SkillStatus.DRAFT
    created_at: str = None
    updated_at: str = None
    published_at: Optional[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at


@dataclass
class SkillReview:
    """User review of a skill"""
    review_id: str
    skill_id: str
    user_id: str
    rating: int  # 1-5
    comment: str
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class Purchase:
    """Skill purchase record"""
    purchase_id: str
    skill_id: str
    user_id: str
    price_paid: float
    currency: str
    purchase_date: str = None
    license_key: str = None
    
    def __post_init__(self):
        if self.purchase_date is None:
            self.purchase_date = datetime.now().isoformat()
        if self.license_key is None:
            self.license_key = self._generate_license()
    
    def _generate_license(self) -> str:
        """Generate unique license key"""
        data = f"{self.skill_id}:{self.user_id}:{self.purchase_date}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


class SkillPackage:
    """
    Manages skill package creation and validation
    """
    
    def __init__(self, skills_dir: str = ".arli/skills"):
        self.skills_dir = Path(skills_dir)
        self.skills_dir.mkdir(parents=True, exist_ok=True)
    
    def create_skill_template(self, name: str, author: str) -> Path:
        """
        Create template for new skill
        """
        skill_id = f"{author.lower().replace(' ', '_')}.{name.lower().replace(' ', '_')}"
        skill_path = self.skills_dir / "source" / skill_id
        skill_path.mkdir(parents=True, exist_ok=True)
        
        # Create skill.py
        skill_py = skill_path / "skill.py"
        skill_py.write_text(f'''#!/usr/bin/env python3
"""
{name} Skill for ARLI
Author: {author}
"""

class Skill:
    """Main skill class"""
    
    def __init__(self, runtime):
        self.runtime = runtime
        self.name = "{name}"
    
    def execute(self, **kwargs):
        """
        Main execution method
        Override this with your skill logic
        """
        # Your skill implementation here
        return {{"success": True, "result": "Skill executed"}}
    
    def get_capabilities(self):
        """Return skill capabilities"""
        return [
            "capability_1",
            "capability_2"
        ]

# Entry point
def create_skill(runtime):
    return Skill(runtime)
''')
        
        # Create skill.json metadata
        skill_json = skill_path / "skill.json"
        metadata = SkillMetadata(
            skill_id=skill_id,
            name=name,
            version="1.0.0",
            description=f"Description of {name} skill",
            category=SkillCategory.OTHER,
            author=author,
            author_id="",
            price=0.0
        )
        skill_json.write_text(json.dumps(asdict(metadata), indent=2, default=str))
        
        # Create README
        readme = skill_path / "README.md"
        readme.write_text(f'''# {name}

## Description

Description of your skill here.

## Installation

```bash
arli skill install {skill_id}
```

## Usage

```python
from runtime import AgentRuntime

agent = AgentRuntime("my-agent")
agent.use_skill("{skill_id}")
result = agent.execute_skill("{skill_id}", param="value")
```

## Capabilities

- Capability 1
- Capability 2

## Author

{author}
''')
        
        # Create requirements.txt
        requirements = skill_path / "requirements.txt"
        requirements.write_text("# Add your dependencies here\n")
        
        print(f"✅ Skill template created at: {skill_path}")
        return skill_path
    
    def validate_skill(self, skill_path: Path) -> Dict[str, Any]:
        """
        Validate skill package before publishing
        """
        errors = []
        warnings = []
        
        # Check required files
        required_files = ["skill.py", "skill.json", "README.md"]
        for file in required_files:
            if not (skill_path / file).exists():
                errors.append(f"Missing required file: {file}")
        
        # Validate metadata
        try:
            metadata = json.loads((skill_path / "skill.json").read_text())
            
            required_fields = ["skill_id", "name", "version", "description", "author", "price"]
            for field in required_fields:
                if field not in metadata:
                    errors.append(f"Missing metadata field: {field}")
            
            # Validate price
            if metadata.get("price", 0) < 0:
                errors.append("Price cannot be negative")
            
            # Check skill.py is valid Python
            try:
                compile((skill_path / "skill.py").read_text(), "skill.py", "exec")
            except SyntaxError as e:
                errors.append(f"Syntax error in skill.py: {e}")
            
            # Check entry point exists
            entry_point = metadata.get("entry_point", "skill.py")
            if not (skill_path / entry_point).exists():
                errors.append(f"Entry point not found: {entry_point}")
                
        except json.JSONDecodeError:
            errors.append("Invalid skill.json format")
        except Exception as e:
            errors.append(f"Error reading metadata: {e}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def package_skill(self, skill_path: Path, output_dir: Path = None) -> Path:
        """
        Package skill into distributable format
        """
        if output_dir is None:
            output_dir = self.skills_dir / "packages"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Read metadata
        metadata = json.loads((skill_path / "skill.json").read_text())
        skill_id = metadata["skill_id"]
        version = metadata["version"]
        
        # Create package filename
        package_name = f"{skill_id}-{version}.tar.gz"
        package_path = output_dir / package_name
        
        # Create tar.gz
        with tarfile.open(package_path, "w:gz") as tar:
            tar.add(skill_path, arcname=skill_id)
        
        # Generate checksum
        checksum = hashlib.sha256(package_path.read_bytes()).hexdigest()
        
        # Create manifest
        manifest = {
            "skill_id": skill_id,
            "version": version,
            "package_file": package_name,
            "checksum": checksum,
            "created_at": datetime.now().isoformat(),
            "file_size": package_path.stat().st_size
        }
        
        manifest_path = output_dir / f"{skill_id}-{version}.manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))
        
        print(f"✅ Packaged: {package_path}")
        return package_path


class Marketplace:
    """
    Skills marketplace for discovery and purchase
    """
    
    def __init__(self, marketplace_dir: str = ".arli/marketplace"):
        self.marketplace_dir = Path(marketplace_dir)
        self.marketplace_dir.mkdir(parents=True, exist_ok=True)
        
        # Subdirectories
        self.listings_dir = self.marketplace_dir / "listings"
        self.reviews_dir = self.marketplace_dir / "reviews"
        self.packages_dir = self.marketplace_dir / "packages"
        self.purchases_dir = self.marketplace_dir / "purchases"
        
        for d in [self.listings_dir, self.reviews_dir, self.packages_dir, self.purchases_dir]:
            d.mkdir(exist_ok=True)
        
        self._load_listings()
    
    def _load_listings(self):
        """Load all skill listings"""
        self.listings: Dict[str, SkillMetadata] = {}
        
        for listing_file in self.listings_dir.glob("*.json"):
            try:
                data = json.loads(listing_file.read_text())
                
                # Convert string enums to actual enum values
                # Handle both "published" and "SkillStatus.PUBLISHED" formats
                if 'status' in data and isinstance(data['status'], str):
                    status_str = data['status']
                    if '.' in status_str:
                        status_str = status_str.split('.')[-1]
                    try:
                        data['status'] = SkillStatus(status_str.lower())
                    except ValueError:
                        pass
                
                if 'category' in data and isinstance(data['category'], str):
                    cat_str = data['category']
                    if '.' in cat_str:
                        cat_str = cat_str.split('.')[-1]
                    try:
                        data['category'] = SkillCategory(cat_str.lower())
                    except ValueError:
                        pass
                
                skill = SkillMetadata(**data)
                self.listings[skill.skill_id] = skill
            except:
                pass
    
    def publish_skill(self, skill_path: Path) -> Dict[str, Any]:
        """
        Publish skill to marketplace
        """
        # Validate first
        validator = SkillPackage()
        validation = validator.validate_skill(skill_path)
        
        if not validation["valid"]:
            return {"success": False, "errors": validation["errors"]}
        
        # Load metadata
        metadata = json.loads((skill_path / "skill.json").read_text())
        skill = SkillMetadata(**metadata)
        skill.status = SkillStatus.PENDING_REVIEW
        skill.updated_at = datetime.now().isoformat()
        
        # Save listing
        listing_file = self.listings_dir / f"{skill.skill_id}.json"
        listing_file.write_text(json.dumps(asdict(skill), indent=2, default=str))
        
        # Package skill
        package_path = validator.package_skill(skill_path, self.packages_dir)
        
        # Update in-memory
        self.listings[skill.skill_id] = skill
        
        print(f"✅ Skill '{skill.name}' submitted for review")
        
        return {
            "success": True,
            "skill_id": skill.skill_id,
            "status": skill.status.value,
            "package": str(package_path)
        }
    
    def approve_skill(self, skill_id: str) -> bool:
        """Approve skill for marketplace (admin)"""
        if skill_id not in self.listings:
            return False
        
        skill = self.listings[skill_id]
        skill.status = SkillStatus.PUBLISHED
        skill.published_at = datetime.now().isoformat()
        
        # Save updated listing
        listing_file = self.listings_dir / f"{skill_id}.json"
        listing_file.write_text(json.dumps(asdict(skill), indent=2, default=str))
        
        print(f"✅ Skill '{skill.name}' published to marketplace")
        return True
    
    def search_skills(self, query: str = None, category: SkillCategory = None,
                     max_price: float = None, min_rating: float = None) -> List[SkillMetadata]:
        """
        Search skills in marketplace
        """
        results = []
        
        for skill in self.listings.values():
            # Only show published skills
            if skill.status != SkillStatus.PUBLISHED:
                continue
            
            # Filter by query
            if query:
                query_lower = query.lower()
                if (query_lower not in skill.name.lower() and
                    query_lower not in skill.description.lower()):
                    continue
            
            # Filter by category
            if category and skill.category != category:
                continue
            
            # Filter by price
            if max_price is not None and skill.price > max_price:
                continue
            
            # Filter by rating
            if min_rating is not None and skill.rating < min_rating:
                continue
            
            results.append(skill)
        
        # Sort by rating (descending)
        results.sort(key=lambda s: (s.rating, s.downloads), reverse=True)
        
        return results
    
    def get_skill(self, skill_id: str) -> Optional[SkillMetadata]:
        """Get skill by ID"""
        return self.listings.get(skill_id)
    
    def purchase_skill(self, skill_id: str, user_id: str) -> Dict[str, Any]:
        """
        Purchase a skill
        """
        skill = self.get_skill(skill_id)
        if not skill:
            return {"error": "Skill not found"}
        
        if skill.status != SkillStatus.PUBLISHED:
            return {"error": "Skill not available"}
        
        # Check if already purchased
        purchase_file = self.purchases_dir / f"{user_id}_{skill_id}.json"
        if purchase_file.exists():
            return {"error": "Already purchased"}
        
        # Create purchase record
        purchase = Purchase(
            purchase_id=f"pur_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            skill_id=skill_id,
            user_id=user_id,
            price_paid=skill.price,
            currency=skill.currency
        )
        
        # Save purchase
        purchase_file.write_text(json.dumps(asdict(purchase), indent=2))
        
        # Update download count
        skill.downloads += 1
        listing_file = self.listings_dir / f"{skill_id}.json"
        listing_file.write_text(json.dumps(asdict(skill), indent=2, default=str))
        
        print(f"✅ Skill '{skill.name}' purchased by {user_id}")
        
        return {
            "success": True,
            "purchase_id": purchase.purchase_id,
            "license_key": purchase.license_key,
            "download_url": f"marketplace://{skill_id}"
        }
    
    def add_review(self, skill_id: str, user_id: str, rating: int, comment: str) -> bool:
        """Add review to skill"""
        skill = self.get_skill(skill_id)
        if not skill:
            return False
        
        review = SkillReview(
            review_id=f"rev_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            skill_id=skill_id,
            user_id=user_id,
            rating=max(1, min(5, rating)),  # Clamp 1-5
            comment=comment
        )
        
        # Save review
        reviews_file = self.reviews_dir / f"{skill_id}.jsonl"
        with open(reviews_file, "a") as f:
            f.write(json.dumps(asdict(review), default=str) + "\n")
        
        # Update skill rating
        self._update_skill_rating(skill_id)
        
        print(f"✅ Review added for '{skill.name}'")
        return True
    
    def _update_skill_rating(self, skill_id: str):
        """Recalculate skill rating from reviews"""
        reviews_file = self.reviews_dir / f"{skill_id}.jsonl"
        if not reviews_file.exists():
            return
        
        ratings = []
        with open(reviews_file) as f:
            for line in f:
                try:
                    review = json.loads(line)
                    ratings.append(review["rating"])
                except:
                    pass
        
        if ratings:
            skill = self.listings[skill_id]
            skill.rating = sum(ratings) / len(ratings)
            skill.review_count = len(ratings)
            
            listing_file = self.listings_dir / f"{skill_id}.json"
            listing_file.write_text(json.dumps(asdict(skill), indent=2, default=str))
    
    def get_revenue_stats(self, author_id: str = None) -> Dict[str, Any]:
        """
        Get revenue statistics
        """
        total_sales = 0
        total_platform_fee = 0
        total_creator_earnings = 0
        
        skill_sales: Dict[str, Dict] = {}
        
        for purchase_file in self.purchases_dir.glob("*.json"):
            try:
                purchase = json.loads(purchase_file.read_text())
                skill_id = purchase["skill_id"]
                
                if skill_id not in self.listings:
                    continue
                
                skill = self.listings[skill_id]
                
                # Filter by author if specified
                if author_id and skill.author_id != author_id:
                    continue
                
                price = purchase["price_paid"]
                platform_fee = price * 0.10  # 10% platform fee
                creator_earnings = price * 0.90  # 90% to creator
                
                total_sales += price
                total_platform_fee += platform_fee
                total_creator_earnings += creator_earnings
                
                if skill_id not in skill_sales:
                    skill_sales[skill_id] = {
                        "name": skill.name,
                        "sales_count": 0,
                        "revenue": 0
                    }
                
                skill_sales[skill_id]["sales_count"] += 1
                skill_sales[skill_id]["revenue"] += creator_earnings
                
            except:
                pass
        
        return {
            "total_sales": total_sales,
            "total_platform_fee": total_platform_fee,
            "total_creator_earnings": total_creator_earnings,
            "skill_breakdown": skill_sales
        }


class SkillInstaller:
    """
    Installs and manages purchased skills
    """
    
    def __init__(self, install_dir: str = ".arli/skills/installed"):
        self.install_dir = Path(install_dir)
        self.install_dir.mkdir(parents=True, exist_ok=True)
    
    def install_skill(self, skill_id: str, marketplace: Marketplace, 
                     user_id: str) -> Dict[str, Any]:
        """
        Install purchased skill
        """
        # Verify purchase
        purchase_file = marketplace.purchases_dir / f"{user_id}_{skill_id}.json"
        if not purchase_file.exists():
            return {"error": "Skill not purchased"}
        
        purchase = json.loads(purchase_file.read_text())
        
        # Get skill metadata
        skill = marketplace.get_skill(skill_id)
        if not skill:
            return {"error": "Skill not found"}
        
        # Find package
        package_file = marketplace.packages_dir / f"{skill_id}-{skill.version}.tar.gz"
        if not package_file.exists():
            return {"error": "Package not found"}
        
        # Extract to install dir
        install_path = self.install_dir / skill_id
        if install_path.exists():
            shutil.rmtree(install_path)
        
        with tarfile.open(package_file, "r:gz") as tar:
            tar.extractall(self.install_dir)
        
        # Save installation record
        install_record = {
            "skill_id": skill_id,
            "version": skill.version,
            "installed_at": datetime.now().isoformat(),
            "purchase_id": purchase["purchase_id"],
            "license_key": purchase["license_key"]
        }
        
        record_file = self.install_dir / f"{skill_id}.installed.json"
        record_file.write_text(json.dumps(install_record, indent=2))
        
        print(f"✅ Skill '{skill.name}' installed successfully")
        
        return {
            "success": True,
            "skill_id": skill_id,
            "install_path": str(install_path),
            "version": skill.version
        }
    
    def load_skill(self, skill_id: str, runtime):
        """
        Load installed skill for use
        """
        install_path = self.install_dir / skill_id
        if not install_path.exists():
            return None
        
        # Check installation record
        record_file = self.install_dir / f"{skill_id}.installed.json"
        if not record_file.exists():
            return None
        
        # Load skill module
        skill_file = install_path / "skill.py"
        if not skill_file.exists():
            return None
        
        # Import skill dynamically
        import importlib.util
        spec = importlib.util.spec_from_file_location(f"skill_{skill_id}", skill_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Create skill instance
        if hasattr(module, 'create_skill'):
            return module.create_skill(runtime)
        elif hasattr(module, 'Skill'):
            return module.Skill(runtime)
        
        return None
    
    def list_installed_skills(self) -> List[Dict]:
        """List all installed skills"""
        installed = []
        
        for record_file in self.install_dir.glob("*.installed.json"):
            try:
                record = json.loads(record_file.read_text())
                installed.append(record)
            except:
                pass
        
        return installed
    
    def uninstall_skill(self, skill_id: str) -> bool:
        """Uninstall a skill"""
        install_path = self.install_dir / skill_id
        record_file = self.install_dir / f"{skill_id}.installed.json"
        
        if install_path.exists():
            shutil.rmtree(install_path)
        
        if record_file.exists():
            record_file.unlink()
        
        print(f"✅ Skill '{skill_id}' uninstalled")
        return True


# Example usage
if __name__ == "__main__":
    print("🚀 ARLI Skills Marketplace Test")
    print("=" * 60)
    
    # Create marketplace
    marketplace = Marketplace()
    
    # Create skill template
    print("\n1. Creating skill template...")
    packager = SkillPackage()
    template_path = packager.create_skill_template(
        name="Web Scraper Pro",
        author="DevStudio One"
    )
    
    # Update metadata for test
    metadata = json.loads((template_path / "skill.json").read_text())
    metadata["skill_id"] = "devstudio.web_scraper_pro"
    metadata["description"] = "Advanced web scraping with anti-detection"
    metadata["category"] = "web_scraping"
    metadata["price"] = 49.99
    metadata["author_id"] = "devstudio_one"
    (template_path / "skill.json").write_text(json.dumps(metadata, indent=2))
    
    # Publish skill
    print("\n2. Publishing skill...")
    result = marketplace.publish_skill(template_path)
    print(f"   Published: {result.get('success')}")
    
    # Approve skill
    print("\n3. Approving skill...")
    marketplace.approve_skill("devstudio.web_scraper_pro")
    
    # Search skills
    print("\n4. Searching skills...")
    results = marketplace.search_skills(query="scraper", max_price=100)
    print(f"   Found {len(results)} skills")
    for skill in results:
        print(f"   • {skill.name} - ${skill.price}")
    
    # Purchase skill
    print("\n5. Purchasing skill...")
    purchase = marketplace.purchase_skill(
        skill_id="devstudio.web_scraper_pro",
        user_id="user_123"
    )
    print(f"   License key: {purchase.get('license_key')}")
    
    # Add review
    print("\n6. Adding review...")
    marketplace.add_review(
        skill_id="devstudio.web_scraper_pro",
        user_id="user_123",
        rating=5,
        comment="Excellent skill, works great!"
    )
    
    # Install skill
    print("\n7. Installing skill...")
    installer = SkillInstaller()
    install_result = installer.install_skill(
        skill_id="devstudio.web_scraper_pro",
        marketplace=marketplace,
        user_id="user_123"
    )
    print(f"   Installed at: {install_result.get('install_path')}")
    
    # Revenue stats
    print("\n8. Revenue statistics...")
    stats = marketplace.get_revenue_stats()
    print(f"   Total sales: ${stats['total_sales']:.2f}")
    print(f"   Platform fee (10%): ${stats['total_platform_fee']:.2f}")
    print(f"   Creator earnings (90%): ${stats['total_creator_earnings']:.2f}")
    
    print("\n✅ Skills Marketplace tests complete!")
