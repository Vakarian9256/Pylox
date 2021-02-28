import time
import decimal
from typing import List, Any
from Lox_callable import LoxCallable

class Clock(LoxCallable):
            def call(self, interpreter, arguments: list[Any]):
                return decimal.Decimal(time.perf_counter())
            
            def arity(self):
                return 0
            
            def __str__(self):
                return "<Native func 'clock'>"