# Root Cause Tracing

## Overview

Bugs often manifest deep in the call stack. Your instinct is to fix where the error appears, but that's treating a symptom.

**Core principle:** Trace backward through the call chain until you find the original trigger, then fix at the source.

## The Tracing Process

1. **Observe the Symptom** - Note the error and where it occurs
2. **Find Immediate Cause** - What code directly causes this?
3. **Ask: What Called This?** - Trace up the call chain
4. **Keep Tracing Up** - What value was passed? Where did it come from?
5. **Find Original Trigger** - The root cause, not the symptom

## Adding Stack Traces

When you can't trace manually, add instrumentation with `new Error().stack` before the problematic operation.

## Key Principle

**NEVER fix just where the error appears.** Trace back to find the original trigger. Then add defense-in-depth validation at each layer.
