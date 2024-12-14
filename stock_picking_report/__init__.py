from . import models
from . import iot_handlers

import logging
from odoo import models
import websocket

# Function to patch enableTrace method
def patch_websocket_enableTrace():
    try:
        original_enableTrace = websocket.enableTrace

        # Define a patched version of enableTrace to fix the 'level' argument issue
        def patched_enableTrace(trace, *args, **kwargs):
            if 'level' in kwargs:
                del kwargs['level']  # Remove 'level' argument
            return original_enableTrace(trace, *args, **kwargs)

        # Replace the original enableTrace with the patched one
        websocket.enableTrace = patched_enableTrace
        _logger = logging.getLogger(__name__)
        _logger.info("WebSocket enableTrace patched successfully.")
    except Exception as e:
        _logger = logging.getLogger(__name__)
        _logger.error(f"Failed to patch WebSocket enableTrace: {e}")

# Apply the patch during module initialization
patch_websocket_enableTrace()
