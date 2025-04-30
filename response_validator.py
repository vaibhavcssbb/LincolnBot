from typing import Dict, List, Any
import re
from datetime import datetime

class ResponseValidator:
    def __init__(self):
        """Initialize response validator."""
        # Define validation rules
        self.rules = {
            "numeric_values": r"\d+",
            "currency": r"£\d+(?:\.\d{2})?",
            "dates": r"\d{2}/\d{2}/\d{2,4}",
            "time": r"\d{1,2}:\d{2}(?:\s*[AaPp][Mm])?",
            "penalty_numbers": r"PN\d{3}",
            "vehicle_registrations": r"[A-Z]{2}\d{2}[A-Z]{3}"
        }
        
        # Define required fields for different query types with synonyms
        self.required_fields = {
            "parking_rules": {
                "time": ["time", "hours", "8am", "6pm"],
                "duration": ["duration", "stay", "hours", "2 hours"],
                "restrictions": ["restrictions", "rules", "cannot", "not allowed"]
            },
            "parking_permits": {
                "cost": ["cost", "price", "fee", "£"],
                "duration": ["duration", "valid", "annual"],
                "requirements": ["requirements", "needed", "required", "proof"]
            },
            "penalties": {
                "amount": ["amount", "fine", "£", "cost"],
                "violation_type": ["violation", "offense", "illegal", "restricted"],
                "payment_deadline": ["deadline", "due", "payment", "pay"]
            }
        }
    
    def validate_response(self, query: str, response: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a response against search results and rules."""
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "missing_fields": [],
            "confidence_score": 1.0
        }
        
        # Extract query type
        query_type = self._get_query_type(query)
        
        # Check for required fields
        if query_type in self.required_fields:
            missing = self._check_required_fields(response, query_type)
            if missing:
                validation_result["missing_fields"] = missing
                validation_result["is_valid"] = False
                validation_result["confidence_score"] -= 0.2 * len(missing)
        
        # Validate against search results
        result_validation = self._validate_against_search_results(response, search_results)
        if not result_validation["is_consistent"]:
            validation_result["warnings"].extend(result_validation["inconsistencies"])
            validation_result["confidence_score"] -= 0.3
        
        # Check for specific patterns
        pattern_validation = self._validate_patterns(response)
        if pattern_validation["warnings"]:
            validation_result["warnings"].extend(pattern_validation["warnings"])
            validation_result["confidence_score"] -= 0.1 * len(pattern_validation["warnings"])
        
        # Ensure confidence score is between 0 and 1
        validation_result["confidence_score"] = max(0.0, min(1.0, validation_result["confidence_score"]))
        
        return validation_result
    
    def _get_query_type(self, query: str) -> str:
        """Determine the type of query."""
        query = query.lower()
        if "rule" in query or "regulation" in query:
            return "parking_rules"
        elif "permit" in query or "pass" in query:
            return "parking_permits"
        elif "penalty" in query or "fine" in query:
            return "penalties"
        return "general"
    
    def _check_required_fields(self, response: str, query_type: str) -> List[str]:
        """Check if response contains all required fields for the query type."""
        missing = []
        response_lower = response.lower()
        
        for field, synonyms in self.required_fields[query_type].items():
            field_found = False
            for synonym in synonyms:
                if synonym in response_lower:
                    field_found = True
                    break
            
            if not field_found:
                missing.append(field)
        
        return missing
    
    def _validate_against_search_results(self, response: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate response against search results."""
        validation = {
            "is_consistent": True,
            "inconsistencies": []
        }
        
        # Extract key information from search results
        search_info = set()
        for result in search_results:
            search_info.update(self._extract_key_info(result["text"]))
        
        # Extract key information from response
        response_info = self._extract_key_info(response)
        
        # Check for inconsistencies
        for info in response_info:
            if info not in search_info:
                validation["inconsistencies"].append(f"Information not found in search results: {info}")
                validation["is_consistent"] = False
        
        return validation
    
    def _validate_patterns(self, response: str) -> Dict[str, List[str]]:
        """Validate response against defined patterns."""
        validation = {
            "warnings": []
        }
        
        for pattern_name, pattern in self.rules.items():
            matches = re.findall(pattern, response)
            if matches:
                # Check if the pattern is used correctly in context
                for match in matches:
                    if not self._validate_pattern_context(match, pattern_name, response):
                        validation["warnings"].append(f"Potential misuse of {pattern_name}: {match}")
        
        return validation
    
    def _extract_key_info(self, text: str) -> set:
        """Extract key information from text."""
        info = set()
        
        # Extract numeric values
        info.update(re.findall(self.rules["numeric_values"], text))
        
        # Extract currency values
        info.update(re.findall(self.rules["currency"], text))
        
        # Extract dates
        info.update(re.findall(self.rules["dates"], text))
        
        # Extract penalty numbers
        info.update(re.findall(self.rules["penalty_numbers"], text))
        
        # Extract vehicle registrations
        info.update(re.findall(self.rules["vehicle_registrations"], text))
        
        return info
    
    def _validate_pattern_context(self, match: str, pattern_name: str, context: str) -> bool:
        """Validate if a pattern match is used correctly in context."""
        # Add specific validation rules for each pattern type
        if pattern_name == "currency":
            # Check if currency is used with a valid amount
            return bool(re.search(r"£\d+(?:\.\d{2})?\s*(?:per|for|cost|fee|amount)", context))
        elif pattern_name == "dates":
            # Check if date is used in a valid context
            return bool(re.search(r"\d{2}/\d{2}/\d{2,4}\s*(?:deadline|due|by|on|date)", context))
        elif pattern_name == "penalty_numbers":
            # Check if penalty number is referenced correctly
            return bool(re.search(r"penalty\s+number\s+" + match, context.lower()))
        
        return True 