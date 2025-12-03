"""
Intent Common Model (ICM) data models.

Based on:
- TMF921 Intent Management v5.0.0 (pages 159-178)
- TR290A Intent Common Model - Intent Expression v3.6.0 (pages 11-26)
- TR290V Vocabulary Reference v3.6.0

Implements TM Forum's JSON-LD based Intent structure with @context and @type.
"""

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class ICMIntent(BaseModel):
    """
    TMF921 Intent using Intent Common Model structure.
    
    Reference: TMF921 v5.0.0, pages 159-178
    TR290A v3.6.0, pages 11-18
    """
    context: str = Field(
        default="http://tio.models.tmforum.org/tio/v3.6.0/context.json",
        alias="@context",
        description="JSON-LD context for TM Forum Intent Ontology"
    )
    type: str = Field(
        default="icm:Intent",
        alias="@type",
        description="RDF type identifier for Intent"
    )
    id: Optional[str] = Field(
        None,
        alias="@id",
        description="Unique identifier for this intent"
    )
    name: str = Field(
        ...,
        description="Human-readable name for the intent"
    )
    description: str = Field(
        ...,
        description="Detailed description of what the intent achieves"
    )
    hasExpectation: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of expectations (Property, Delivery, Reporting)"
    )
    target: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Target resources for this intent"
    )
    
    class Config:
        populate_by_name = True  # Allow both 'context' and '@context'
        json_schema_extra = {
            "example": {
                "@context": "http://tio.models.tmforum.org/tio/v3.6.0/context.json",
                "@type": "icm:Intent",
                "@id": "#gaming-slice-intent",
                "name": "Gaming Network Slice",
                "description": "High-performance network slice for gaming applications",
                "hasExpectation": [
                    {
                        "@type": "icm:PropertyExpectation",
                        "target": {"@id": "#target1"}
                    }
                ],
                "target": [
                    {
                        "@id": "#target1",
                        "@type": "icm:Target",
                        "resourceType": "NetworkSlice"
                    }
                ]
            }
        }


class PropertyExpectation(BaseModel):
    """
    Property expectation specifying desired characteristics.
    
    Reference: TR290A v3.6.0, pages 13-16
    """
    type: str = Field(
        default="icm:PropertyExpectation",
        alias="@type"
    )
    id: Optional[str] = Field(None, alias="@id")
    target: Dict[str, str] = Field(
        ...,
        description="Reference to target (@id)"
    )
    expectationCondition: Optional[Dict[str, Any]] = Field(
        None,
        description="Condition specifying the property requirements"
    )
    
    class Config:
        populate_by_name = True


class DeliveryExpectation(BaseModel):
    """
    Delivery expectation specifying what should be delivered.
    
    Reference: TR290A v3.6.0, pages 17-19
    """
    type: str = Field(
        default="icm:DeliveryExpectation",
        alias="@type"
    )
    id: Optional[str] = Field(None, alias="@id")
    target: Dict[str, str] = Field(..., description="Reference to target")
    targetType: str = Field(
        ...,
        description="Type of resource to deliver (e.g., NetworkSlice)"
    )
    
    class Config:
        populate_by_name = True


class ReportingExpectation(BaseModel):
    """
    Reporting expectation specifying how intent status should be reported.
    
    Reference: TR290B v3.6.0, pages 17-20
    """
    type: str = Field(
        default="icm:ReportingExpectation",
        alias="@type"
    )
    id: Optional[str] = Field(None, alias="@id")
    target: Dict[str, str] = Field(..., description="Reference to intent")
    reportDestination: List[str] = Field(
        default_factory=list,
        description="Where reports should be sent"
    )
    reportTriggers: List[str] = Field(
        default_factory=list,
        description="Events that trigger reports (e.g., imo:IntentAccepted)"
    )
    
    class Config:
        populate_by_name = True


class Target(BaseModel):
    """
    Target identifies resources that the intent applies to.
    
    Reference: TR290A v3.6.0, pages 20-23
    """
    id: str = Field(..., alias="@id", description="Unique identifier")
    type: str = Field(
        default="icm:Target",
        alias="@type"
    )
    resourceType: Optional[str] = Field(
        None,
        description="Type of resource (e.g., NetworkSlice, Service)"
    )
    chooseFrom: Optional[Dict[str, Any]] = Field(
        None,
        description="Set operator defining resource selection"
    )
    
    class Config:
        populate_by_name = True


class Condition(BaseModel):
    """
    Condition specifies constraints using quantity/logical operators.
    
    Reference: TR292E v3.6.0 (Conditions and Logical Operators)
    """
    type: str = Field(
        default="log:Condition",
        alias="@type"
    )
    id: Optional[str] = Field(None, alias="@id")
    
    # Quantity operators (TR292D)
    smaller: Optional[Dict[str, Any]] = Field(
        None,
        alias="quan:smaller",
        description="Less than constraint"
    )
    greater: Optional[Dict[str, Any]] = Field(
        None,
        alias="quan:greater",
        description="Greater than constraint"
    )
    equal: Optional[Dict[str, Any]] = Field(
        None,
        alias="quan:equal",
        description="Equality constraint"
    )
    
    # Logical operators (TR292E)
    allOf: Optional[List[Dict[str, Any]]] = Field(
        None,
        alias="log:allOf",
        description="All conditions must be true (AND)"
    )
    anyOf: Optional[List[Dict[str, Any]]] = Field(
        None,
        alias="log:anyOf",
        description="At least one condition must be true (OR)"
    )
    
    class Config:
        populate_by_name = True


class IntentReport(BaseModel):
    """
    Intent Report for lifecycle status reporting.
    
    Reference: TR290B v3.6.0, pages 17-20
    TMF921 v5.0.0, pages 179-195
    """
    context: str = Field(
        default="http://tio.models.tmforum.org/tio/v3.6.0/context.json",
        alias="@context"
    )
    type: str = Field(
        default="icm:IntentReport",
        alias="@type"
    )
    id: Optional[str] = Field(None, alias="@id")
    about: str = Field(
        ...,
        description="Reference to the Intent being reported on"
    )
    reportTimestamp: datetime = Field(
        ...,
        description="When this report was generated"
    )
    reportHandlingState: str = Field(
        ...,
        description="Current handling state (e.g., StateAccepted, StateCompliant)"
    )
    updateState: str = Field(
        default="StateNoUpdate",
        description="Whether this is an update (StateUpdate) or no change"
    )
    reportNumber: int = Field(
        default=1,
        description="Sequential report number"
    )
    expectationReports: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Status of individual expectations"
    )
    
    class Config:
        populate_by_name = True
