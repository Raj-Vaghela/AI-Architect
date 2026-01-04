# Stack8s Database Analysis Dashboard

A static HTML/CSS/JS dashboard that visualizes the database profiling findings for the Stack8s AI Architect project.

## Features

- **Overview**: Project summary, quick stats, and provider distribution charts
- **Compute Instances**: Trusted fields, data coverage, GPU analysis, pricing insights
- **Marketplace Packages**: Category distribution, keyword analysis, proposed AI taxonomy
- **Data Contract**: Supported/unsupported decisions, input schemas, limitations

## Quick Start

### Option 1: Direct File Open (May Have CORS Issues)

Simply open `dashboard/index.html` in your browser:

```bash
# Navigate to the dashboard directory
cd dashboard

# Open in default browser (macOS)
open index.html

# Open in default browser (Windows)
start index.html

# Open in default browser (Linux)
xdg-open index.html
```

⚠️ **Note:** Most modern browsers block local file access for security reasons. If you see an error, use Option 2.

### Option 2: Local Web Server (Recommended)

Start a simple HTTP server to avoid CORS restrictions:

**Using Python 3:**
```bash
# From the project root directory (E:\Stack8s)
python -m http.server 8000

# Then open in browser:
# http://localhost:8000/dashboard/index.html
```

**Using Python 2:**
```bash
python -m SimpleHTTPServer 8000
```

**Using Node.js (if you have npx):**
```bash
npx http-server -p 8000

# Then open: http://localhost:8000/dashboard/index.html
```

**Using PHP:**
```bash
php -S localhost:8000

# Then open: http://localhost:8000/dashboard/index.html
```

## Project Structure

```
dashboard/
├── index.html          # Main HTML structure
├── styles.css          # Styling and layout
├── app.js              # JavaScript logic, data loading, and charts
└── README.md           # This file

docs/                   # Data sources (markdown files)
├── db-map.md
├── instances-profile.md
├── packages-profile.md
└── v1-data-contract.md
```

## How It Works

1. **Data Loading**: The dashboard loads markdown files from `../docs/` at runtime using `fetch()`
2. **Parsing**: Extracts key metrics, tables, and insights from markdown content
3. **Visualization**: Renders data as cards, stats, and charts (vanilla canvas-based)
4. **Navigation**: Single-page app with sidebar navigation

## Data Sources

The dashboard reads data from these markdown files:

- **`docs/db-map.md`**: Complete database schema map with table descriptions and relationships
- **`docs/instances-profile.md`**: Detailed profiling of compute instances table (16,695 rows)
- **`docs/packages-profile.md`**: Marketplace packages analysis (13,435 packages)
- **`docs/v1-data-contract.md`**: V1 data contract defining what AI can/cannot recommend

## Key Metrics Displayed

### Overview
- Total instances: 16,695
- Total packages: 13,435
- Cloud providers: 7 (AWS, OVH, Vultr, DigitalOcean, Contabo, RunPod, Civo)
- Geographic regions: 234

### Compute Instances
- **Trusted fields**: provider (100%), vCPU (99.7%), RAM (99.7%), price (98.5%)
- **Critical gaps**: GPU model (4.7%), GPU VRAM (4.8%), GPU manufacturer (0%)
- **Provider distribution**: AWS 89%, OVH 8.1%, Vultr 1.2%, others <1%
- **GPU instances**: 728 (4.4% of total)

### Marketplace Packages
- **Good coverage**: description (99.5%), version (100%), install URL (100%)
- **Critical gaps**: categories (31.9%), keywords (42% populated)
- **Uncategorized**: 9,145 packages (68%)
- **Proposed**: 13-category AI stack taxonomy

### Data Contract
- **V1 Supported**: Filter by provider, vCPU, RAM, price, GPU count, region
- **V1 Unsupported**: Filter by GPU model, VRAM, AI stack components
- **Proposed fixes**: gpu_specs mapping table, component_tags system

## Browser Compatibility

Tested and working on:
- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+

**Requirements:**
- JavaScript enabled
- Local file access OR local web server
- Canvas support

## Troubleshooting

### Issue: "Unable to Load Data" error

**Cause:** Browser security blocks local file access via `fetch()`

**Solution:** Use a local web server (see Option 2 above)

### Issue: Charts not displaying

**Cause:** Canvas not supported or JavaScript disabled

**Solution:** 
1. Enable JavaScript in browser settings
2. Use a modern browser (Chrome, Firefox, Safari)
3. Check browser console for errors

### Issue: Styling looks broken

**Cause:** CSS file not loading

**Solution:**
1. Ensure `styles.css` is in the same directory as `index.html`
2. Use a local web server instead of direct file open
3. Check browser console for 404 errors

## Development

### File Modifications

- **Update stats**: Edit the hardcoded values in `app.js` (functions: `extractOverviewStats()`, chart data)
- **Add sections**: Add new section HTML in `index.html`, add rendering function in `app.js`
- **Styling**: Modify `styles.css` using CSS variables (defined in `:root`)

### Adding New Charts

Example of adding a chart:

```javascript
// In app.js
function drawMyChart() {
    const canvas = document.getElementById('my-chart');
    const ctx = canvas.getContext('2d');
    
    const data = [
        { name: 'Item 1', count: 100, color: '#3b82f6' },
        { name: 'Item 2', count: 200, color: '#10b981' }
    ];
    
    drawBarChart(ctx, canvas, data, 'My Chart Title');
}
```

```html
<!-- In index.html -->
<div class="card">
    <h2>My Chart</h2>
    <canvas id="my-chart" width="800" height="300"></canvas>
</div>
```

## No External Dependencies

This dashboard uses:
- ✅ **Zero npm packages**
- ✅ **Zero frameworks** (React, Vue, etc.)
- ✅ **Zero build tools** (webpack, vite, etc.)
- ✅ **Pure vanilla JavaScript**
- ✅ **Native Canvas API** for charts

Everything runs directly in the browser!

## Future Enhancements

Potential improvements (not implemented):

- [ ] Live data fetching from Supabase (would require API keys)
- [ ] Interactive chart filtering (click to drill down)
- [ ] Export to PDF/PNG
- [ ] Dark mode toggle
- [ ] Search functionality across all sections
- [ ] Real-time data refresh

## License

Part of the Stack8s project. See main project LICENSE.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all markdown files exist in `../docs/`
3. Check browser console for errors
4. Ensure local web server is running (if needed)

---

**Last Updated:** 2025-12-25  
**Version:** 1.0  
**Author:** Stack8s Team


