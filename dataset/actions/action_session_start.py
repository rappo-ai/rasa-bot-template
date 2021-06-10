from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, EventType

from actions.utils.json import get_json_key
from actions.utils.telegram import get_chat_type

class ActionSessionStart(Action):
    def name(self) -> Text:
        return "action_session_start"

    @staticmethod
    def fetch_previous_slots(tracker: Tracker) -> List[EventType]:
        """Collect all prior slots"""

        slots = []
        for key in tracker.slots.keys():
            value = tracker.get_slot(key)
            if (value is not None) and (key is not "session_started_metadata"):
                slots.append(SlotSet(key=key, value=value))
        return slots
        
        """for event in tracker.events:
            if event.event == "slot":
                if event.value is not None:
                    slots[event.name] = SlotSet(key=event.name, value=event.value, timestamp=event.timestamp)
            elif event.event == "restart":
                session_started_metadata_slot = slots["session_started_metadata"]
                slots = {}
                if session_started_metadata_slot is not None:
                    slots["session_started_metadata"] = session_started_metadata_slot
            
        return list(slots.values())"""

    @staticmethod
    def fetch_telegram_slots(tracker: Tracker) -> List[EventType]:
        """Add Telegram-specific slots"""

        metadata = tracker.get_slot("session_started_metadata")

        slots = []
        
        chat_type = get_chat_type(metadata)
        if chat_type is not None:
            slots.append(SlotSet(key="chat_type", value=chat_type))

        return slots

    async def run(
      self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        # the session should begin with a `session_started` event
        events = [SessionStarted()]

        # any slots that should be carried over should come after the
        # `session_started` event
        if get_json_key(domain, "session_config.carry_over_slots_to_new_session", True):
            events.extend(self.fetch_previous_slots(tracker))

        # add slots specific to Telegram platform
        events.extend(self.fetch_telegram_slots(tracker))

        # an `action_listen` should be added at the end as a user message follows
        events.append(ActionExecuted("action_listen"))

        return events