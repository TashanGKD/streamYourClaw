# Contributing Status Videos

This guide explains how to contribute status videos to streamYourClaw.

## Overview

Status videos are visual indicators that show the current state of the AI agent. They appear in the bottom-left corner of the live stream interface.

## Available States

| State | Description | Default Color |
|-------|-------------|---------------|
| `typing` | Agent is inputting/typing | Blue (#58a6ff) |
| `waiting` | Agent is waiting for results | Purple (#a371f7) |
| `thinking` | Agent is processing | Yellow (#d29922) |

## Video Requirements

### Technical Specifications

| Property | Requirement | Recommended |
|----------|-------------|-------------|
| Format | MP4 (H.264) | MP4 |
| Resolution | 300x300 - 800x800 | 400x400 or 600x600 |
| Aspect Ratio | 1:1 (square) | 1:1 |
| Duration | 2-10 seconds | 3-5 seconds |
| Frame Rate | 24-60 FPS | 30 FPS |
| File Size | < 10 MB | < 5 MB |
| Audio | No audio (muted) | - |

### Content Guidelines

- **Loop-friendly**: Videos should loop seamlessly
- **Clear action**: The action/state should be immediately recognizable
- **Appropriate**: Content suitable for all audiences (TikTok guidelines)
- **Original**: Only submit content you created or have rights to

## Step-by-Step Contribution

### 1. Prepare Your Video

```bash
# Example: Convert and optimize with ffmpeg
ffmpeg -i input.mov -vf "scale=400:400:force_original_aspect_ratio=decrease,pad=400:400:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -pix_fmt yuv420p -an output.mp4
```

### 2. Add to Project

Place your video in the appropriate directory:

```
frontend/assets/videos/
├── meta.json
├── typing_01.mp4
├── typing_02.mp4      # Your new video
├── waiting_01.mp4
└── thinking_01.mp4
```

### 3. Update Configuration

Edit `frontend/assets/videos/meta.json`:

```json
{
  "version": "1.0",
  "states": {
    "typing": {
      "name": "Typing",
      "description": "Agent is inputting text",
      "videos": [
        {
          "file": "typing_01.mp4",
          "duration": 3000,
          "weight": 1.0
        },
        {
          "file": "typing_02.mp4",    // Your addition
          "duration": 4000,
          "weight": 0.8,              // Lower weight = less frequent
          "author": "YourName",       // Optional attribution
          "source": "https://..."     // Optional source URL
        }
      ],
      "indicatorColor": "#58a6ff"
    }
  }
}
```

### 4. Configuration Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | string | Yes | Video filename |
| `duration` | number | No | Duration in ms (auto-detected if omitted) |
| `weight` | number | No | Selection weight (default: 1.0) |
| `author` | string | No | Contributor attribution |
| `source` | string | No | Original source URL |

### 5. Test Locally

```bash
# Start frontend server
cd frontend
python -m http.server 8080
```

Open `http://localhost:8080` and verify your video displays correctly.

### 6. Submit Pull Request

```bash
git add frontend/assets/videos/your_video.mp4
git add frontend/assets/videos/meta.json
git commit -m "[Video] Add your_video.mp4 for typing state"
git push origin your-branch
```

## Tips for Great Videos

1. **Keep it simple**: One clear action per video
2. **Smooth loops**: Ensure start/end frames match
3. **Good contrast**: Works well on dark backgrounds
4. **Consistent style**: Match existing video aesthetic
5. **Optimize size**: Compress without quality loss

## Example PR Template

```markdown
## Video Contribution

**State**: typing
**Video Name**: typing_coffee.mp4

### Description
A video showing the agent drinking coffee while typing.

### Video Details
- Resolution: 400x400
- Duration: 3.5 seconds
- Size: 1.2 MB

### Checklist
- [x] Video follows technical requirements
- [x] Content is appropriate
- [x] meta.json updated
- [x] Tested locally
```

## Questions?

Open an issue with `[Video]` prefix for any questions about video contributions.