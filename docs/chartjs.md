# Chart.js Integration

This document explains how Chart.js is integrated into the admin dashboard for analytics visualization.

## Setup

### CDN Approach (No Build Step)
Chart.js is loaded via CDN in `dashboard/base.html`:

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
```

**Why CDN?**
- No npm install or build configuration needed
- Browser caches the library across visits
- ~60KB gzipped, loaded asynchronously

## Creating a Chart

### 1. Add a canvas element

```html
<canvas id="myChart" style="max-height: 250px;"></canvas>
```

### 2. Initialize with JavaScript

```html
<script>
new Chart(document.getElementById('myChart'), {
  type: 'doughnut',  // or 'pie', 'bar', 'line'
  data: {
    labels: ['Label 1', 'Label 2'],
    datasets: [{
      data: [10, 20],
      backgroundColor: ['#154734', '#FFB81C']
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: true
  }
});
</script>
```

## Passing Django Data to Charts

Use Django template tags inside the JavaScript:

```html
<script>
new Chart(document.getElementById('categoryChart'), {
  type: 'doughnut',
  data: {
    labels: [
      {% for cat in categories %}
        '{{ cat.name }}'{% if not forloop.last %},{% endif %}
      {% endfor %}
    ],
    datasets: [{
      data: [
        {% for cat in categories %}
          {{ cat.product_count }}{% if not forloop.last %},{% endif %}
        {% endfor %}
      ],
      backgroundColor: ['#154734', '#FFB81C', '#1a5a42', '#d4a017', '#0d2e22']
    }]
  }
});
</script>
```

## Theme Colors

Use Baylor brand colors for consistency:

| Color | Hex | Usage |
|-------|-----|-------|
| BU Green | `#154734` | Primary segments |
| BU Gold | `#FFB81C` | Accent/highlight |
| Green Dark | `#0d2e22` | Additional segments |
| Green Light | `#1a5a42` | Additional segments |
| Gold Dark | `#d4a017` | Additional segments |

## Chart Types

| Type | Best For |
|------|----------|
| `doughnut` | Category distribution, percentages |
| `pie` | Simple two-part comparisons |
| `bar` | Comparing quantities across categories |
| `line` | Trends over time |

## Common Options

```javascript
options: {
  responsive: true,           // Resize with container
  maintainAspectRatio: true,  // Keep proportions
  plugins: {
    legend: {
      position: 'right',      // 'top', 'bottom', 'left', 'right'
      display: true
    },
    tooltip: {
      enabled: true           // Hover tooltips
    }
  }
}
```

## Resources

- [Chart.js Documentation](https://www.chartjs.org/docs/latest/)
- [Doughnut/Pie Charts](https://www.chartjs.org/docs/latest/charts/doughnut.html)
- [Bar Charts](https://www.chartjs.org/docs/latest/charts/bar.html)
