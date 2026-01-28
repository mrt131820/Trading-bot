
class ClassMapper(object):

	def __init__(self):
		from SmartAPI.common.RESOURCE import RESOURCE
		from SmartAPI.model.Ability import Ability
		from SmartAPI.model.AbstractEntity import AbstractEntity
		from SmartAPI.model.Activity import Activity
		from SmartAPI.model.Address import Address
		from SmartAPI.model.AliveRequest import AliveRequest
		from SmartAPI.model.AliveResponse import AliveResponse
		from SmartAPI.model.Capacity import Capacity
		from SmartAPI.model.Condition import Condition
		from SmartAPI.model.Controllability import Controllability
		from SmartAPI.model.Coordinates import Coordinates
		from SmartAPI.model.Device import Device
		from SmartAPI.model.Direction import Direction
		from SmartAPI.model.Entity import Entity
		from SmartAPI.model.Error import Error
		from SmartAPI.model.Evaluation import Evaluation
		from SmartAPI.model.Input import Input
		from SmartAPI.model.InterfaceAddress import InterfaceAddress
		from SmartAPI.model.Map import Map
		from SmartAPI.model.Message import Message
		from SmartAPI.model.Notification import Notification
		from SmartAPI.model.Obj import Obj
		from SmartAPI.model.Organization import Organization
		from SmartAPI.model.Orientation import Orientation
		from SmartAPI.model.Output import Output
		from SmartAPI.model.Parameter import Parameter
		from SmartAPI.model.Person import Person
		from SmartAPI.model.PhysicalEntity import PhysicalEntity
		from SmartAPI.model.Provenance import Provenance
		from SmartAPI.model.Request import Request
		from SmartAPI.model.Response import Response
		from SmartAPI.model.Ring import Ring
		from SmartAPI.model.Route import Route
		from SmartAPI.model.Service import Service
		from SmartAPI.model.ServiceProvider import ServiceProvider
		from SmartAPI.model.Size import Size
		from SmartAPI.model.Status import Status
		from SmartAPI.model.SystemOfInterest import SystemOfInterest
		from SmartAPI.model.TemporalContext import TemporalContext
		from SmartAPI.model.TimeSeries import TimeSeries
		from SmartAPI.model.ValueObject import ValueObject
		from SmartAPI.model.Velocity import Velocity
		from SmartAPI.model.Waypoint import Waypoint
		from SmartAPI.model.Waypoints import Waypoints
		from SmartAPI.model.Zone import Zone
		from SmartAPI.model.UnitPriceSpecification import UnitPriceSpecification
		from SmartAPI.model.Enumeration import Enumeration
		from SmartAPI.model.Transaction import Transaction
		from SmartAPI.model.SomeItems import SomeItems
		from SmartAPI.model.Offering import Offering

		
		self.class_map = {
			RESOURCE.GEO_POINT: Coordinates,
			RESOURCE.ABILITY: Ability,
			RESOURCE.ABSTRACTENTITY: AbstractEntity,
			RESOURCE.ACTIVITY: Activity,
			RESOURCE.ADDRESS: Address,
			RESOURCE.ALIVEREQUEST: AliveRequest,
			RESOURCE.ALIVERESPONSE: AliveResponse,
			RESOURCE.CAPACITY: Capacity,
			RESOURCE.CONDITION: Condition,
			RESOURCE.CONTROLLABILITY: Controllability,
			RESOURCE.DEVICE: Device,
			RESOURCE.DIRECTION: Direction,
			RESOURCE.ENTITY: Entity,
			RESOURCE.ERROR: Error,
			RESOURCE.EVALUATION: Evaluation,
			RESOURCE.ENUMERATION: Enumeration,			
			RESOURCE.INPUT: Input,
			RESOURCE.INTERFACEADDRESS: InterfaceAddress,
			RESOURCE.MAP: Map,
			RESOURCE.MESSAGE: Message,
			RESOURCE.NOTIFICATION: Notification,
			RESOURCE.OBJECT: Obj,
			RESOURCE.OFFERING: Offering,
			RESOURCE.ORGANIZATION: Organization,
			RESOURCE.ORIENTATION: Orientation,
			RESOURCE.OUTPUT: Output,
			RESOURCE.PARAMETER: Parameter,
			RESOURCE.PHYSICALENTITY: PhysicalEntity,
			RESOURCE.PERSON: Person,
			RESOURCE.PROVENANCE: Provenance,
			RESOURCE.REQUEST: Request,
			RESOURCE.RESPONSE: Response,
			RESOURCE.RING: Ring,
			RESOURCE.ROUTE: Route,
			RESOURCE.SERVICE: Service,
			RESOURCE.SERVICEPROVIDER: ServiceProvider,
			RESOURCE.SIZE: Size,
			RESOURCE.SOMEITEMS: SomeItems,				
			RESOURCE.STATUS: Status,
			RESOURCE.SYSTEMOFINTEREST: SystemOfInterest,
			RESOURCE.TEMPORALCONTEXT: TemporalContext,
			RESOURCE.TIMESERIES: TimeSeries,
			RESOURCE.TRANSACTION: Transaction,
			RESOURCE.UNITPRICESPECIFICATION: UnitPriceSpecification,
			RESOURCE.VALUEOBJECT: ValueObject,
			RESOURCE.VELOCITY: Velocity,					
	#		RESOURCE.VARIANT: Variant,
			RESOURCE.WAYPOINT: Waypoint,
			RESOURCE.WAYPOINTS: Waypoints,
			RESOURCE.ZONE: Zone
		}	
			
	def getClass(self, typelist, default = None):
		for t in typelist:
			if self.class_map.has_key(t):
				return self.class_map[t]
		
		# No match, return default
		return default
