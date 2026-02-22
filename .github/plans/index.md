# DevMetrics Wiki

Welcome to the **DevMetrics Dashboard** project wiki — the single source of truth for planning, requirements, specifications, and sprint reviews.

## Sections

| Section | Description |
|---------|-------------|
| [Planning](planning/index.md) | Project plans, roadmaps, and architecture decisions |
| [Requirements](requirements/index.md) | Feature requirements and acceptance criteria |
| [Specifications](specifications/index.md) | Technical specifications and data schemas |
| [Sprint Reviews](sprint-reviews/index.md) | Sprint review summaries and retrospective notes |

## About This Wiki

This wiki is **auto-generated** from markdown files using [DocFX](https://dotnet.github.io/docfx/). Any `.md` file added to the section folders above is automatically included in the next build.

### Contributing

1. Add your markdown file to the appropriate section folder under `.github/plans/`
2. Update the section's `toc.yml` to include your new page
3. Push to the `preview` branch — the wiki rebuilds automatically via GitHub Actions

### Local Preview

```bash
# Install DocFX (requires .NET SDK 8.0+)
dotnet tool install -g docfx

# Build and serve locally
docfx .github/plans/docfx.json --serve
# Open http://localhost:8080
```

## Team

This wiki is maintained by **Martinez** (Product Manager). See the [team roster](../../.squad/team.md) for all squad members.
