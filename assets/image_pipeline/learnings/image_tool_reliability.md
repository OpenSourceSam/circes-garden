# Learning Note: Image Metadata Reliability

## What We Tested

We compared:

1. MiniMax image recognition (`mcp__MiniMax__understand_image`)
2. Native local pixel inspection (Pillow script)

on generated game assets for:
- dimensions
- transparency (alpha)
- background characteristics

## Outcome

For technical metadata, local pixel inspection was more reliable.

MiniMax produced incorrect values on multiple checks (especially exact dimensions and transparency), while local parsing returned deterministic file truth.

## Rule Going Forward

For game integration tasks that require exact technical values:
- frame sizes
- sheet grid math
- alpha/transparency checks
- import pipeline decisions

Use **local scripted inspection** (Pillow/CLI) as source-of-truth.

For this project, image-recognition assessment tools are now **disabled by process** and should not be used for asset validation.  
All validation should be done through local scripts, Godot runtime checks, and headed screenshots.

## Why This Matters

This prevents repeated re-testing and avoids wiring bugs caused by incorrect inferred image properties.

## Quick Reusable Approach

Use a local script that reports:
- width/height
- alpha min/max
- transparent vs opaque pixel stats
- optional color distribution checks

Store findings in commit messages or docs when they become stable workflow rules.
