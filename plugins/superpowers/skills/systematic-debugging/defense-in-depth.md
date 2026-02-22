# Defense-in-Depth Validation

## Overview

When you fix a bug caused by invalid data, adding validation at one place feels sufficient. But that single check can be bypassed by different code paths, refactoring, or mocks.

**Core principle:** Validate at EVERY layer data passes through. Make the bug structurally impossible.

## The Four Layers

1. **Entry Point Validation** - Reject obviously invalid input at API boundary
2. **Business Logic Validation** - Ensure data makes sense for this operation
3. **Environment Guards** - Prevent dangerous operations in specific contexts
4. **Debug Instrumentation** - Capture context for forensics

## Applying the Pattern

When you find a bug:
1. Trace the data flow
2. Map all checkpoints
3. Add validation at each layer
4. Test each layer

**Don't stop at one validation point.** Add checks at every layer.
