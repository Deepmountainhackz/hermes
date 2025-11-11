import streamlit as st
from typing import Callable
import logging

logger = logging.getLogger(__name__)

def cache_data(ttl: int = 300, show_spinner: bool = True):
    def decorator(func: Callable) -> Callable:
        return st.cache_data(ttl=ttl, show_spinner=show_spinner)(func)
    return decorator

def cache_resource(show_spinner: bool = False):
    def decorator(func: Callable) -> Callable:
        return st.cache_resource(show_spinner=show_spinner)(func)
    return decorator

def clear_all_caches():
    st.cache_data.clear()
    st.cache_resource.clear()
    logger.info("All caches cleared")
