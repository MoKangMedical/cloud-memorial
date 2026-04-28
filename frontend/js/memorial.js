/**
 * 念念 - 纪念页交互组件
 * 虚拟蜡烛、虚拟献花、纪念墙
 */

// ===== 虚拟蜡烛系统 =====
class CandleSystem {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        this.candles = [];
        this.animating = false;
        this.resize();
        window.addEventListener('resize', () => this.resize());
    }

    resize() {
        if (!this.canvas) return;
        this.canvas.width = this.canvas.offsetWidth;
        this.canvas.height = this.canvas.offsetHeight;
    }

    addCandle(x, y, type = 'white', message = '') {
        const candle = {
            x, y, type, message,
            flame: 1.0,
            flicker: Math.random() * Math.PI * 2,
            created: Date.now(),
        };
        this.candles.push(candle);
        if (!this.animating) this.animate();
        return candle;
    }

    animate() {
        if (!this.canvas || this.candles.length === 0) {
            this.animating = false;
            return;
        }
        this.animating = true;
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        for (const candle of this.candles) {
            this.drawCandle(candle);
            candle.flicker += 0.05;
        }

        requestAnimationFrame(() => this.animate());
    }

    drawCandle(candle) {
        const ctx = this.ctx;
        const { x, y, type, flicker } = candle;

        // Candle body
        const colors = {
            white: '#f5f0e8',
            red: '#c0392b',
            gold: '#f39c12',
            lotus: '#e91e63',
        };
        ctx.fillStyle = colors[type] || colors.white;
        ctx.fillRect(x - 4, y - 30, 8, 30);

        // Wick
        ctx.strokeStyle = '#333';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(x, y - 30);
        ctx.lineTo(x, y - 35);
        ctx.stroke();

        // Flame
        const flameHeight = 12 + Math.sin(flicker) * 3;
        const flameWidth = 4 + Math.sin(flicker * 1.5) * 1.5;

        // Outer glow
        const gradient = ctx.createRadialGradient(x, y - 35 - flameHeight / 2, 0, x, y - 35 - flameHeight / 2, flameHeight);
        gradient.addColorStop(0, 'rgba(255, 200, 50, 0.8)');
        gradient.addColorStop(0.5, 'rgba(255, 150, 30, 0.4)');
        gradient.addColorStop(1, 'rgba(255, 100, 0, 0)');
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.ellipse(x, y - 35 - flameHeight / 2, flameWidth * 2, flameHeight, 0, 0, Math.PI * 2);
        ctx.fill();

        // Inner flame
        ctx.fillStyle = 'rgba(255, 255, 200, 0.9)';
        ctx.beginPath();
        ctx.ellipse(x, y - 35 - flameHeight * 0.4, flameWidth * 0.5, flameHeight * 0.5, 0, 0, Math.PI * 2);
        ctx.fill();
    }

    clear() {
        this.candles = [];
        if (this.ctx) {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        }
    }
}

// ===== 虚拟献花系统 =====
class FlowerSystem {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.flowers = [];
    }

    offer(flowerType = 'chrysanthemum', message = '') {
        if (!this.container) return;

        const flower = document.createElement('div');
        flower.className = 'flower-offering';
        flower.innerHTML = this.getFlowerSVG(flowerType);

        // Random position
        const x = Math.random() * 80 + 10;
        const y = Math.random() * 60 + 20;
        flower.style.left = x + '%';
        flower.style.top = y + '%';
        flower.style.animation = `flowerAppear 1s ease-out`;

        if (message) {
            const msg = document.createElement('div');
            msg.className = 'flower-message';
            msg.textContent = message;
            flower.appendChild(msg);
        }

        this.container.appendChild(flower);
        this.flowers.push(flower);

        // Auto remove after 30 seconds
        setTimeout(() => {
            flower.style.animation = 'flowerFade 2s ease-in forwards';
            setTimeout(() => flower.remove(), 2000);
        }, 30000);
    }

    getFlowerSVG(type) {
        const flowers = {
            chrysanthemum: `<svg viewBox="0 0 60 60" width="40" height="40">
                <circle cx="30" cy="30" r="8" fill="#f1c40f"/>
                ${Array.from({length: 8}, (_, i) => {
                    const angle = i * Math.PI / 4;
                    const x = 30 + Math.cos(angle) * 15;
                    const y = 30 + Math.sin(angle) * 15;
                    return `<ellipse cx="${x}" cy="${y}" rx="8" ry="4" fill="#f39c12" transform="rotate(${i*45} ${x} ${y})"/>`;
                }).join('')}
            </svg>`,
            lily: `<svg viewBox="0 0 60 60" width="40" height="40">
                <ellipse cx="30" cy="30" rx="6" ry="15" fill="#fff" stroke="#e91e63" stroke-width="1"/>
                <ellipse cx="22" cy="28" rx="6" ry="12" fill="#fff" stroke="#e91e63" stroke-width="1" transform="rotate(-30 22 28)"/>
                <ellipse cx="38" cy="28" rx="6" ry="12" fill="#fff" stroke="#e91e63" stroke-width="1" transform="rotate(30 38 28)"/>
                <circle cx="30" cy="30" r="3" fill="#f1c40f"/>
            </svg>`,
            rose: `<svg viewBox="0 0 60 60" width="40" height="40">
                <circle cx="30" cy="25" r="12" fill="#e74c3c"/>
                <circle cx="30" cy="25" r="8" fill="#c0392b"/>
                <circle cx="30" cy="25" r="4" fill="#e74c3c"/>
                <rect x="29" y="35" width="2" height="20" fill="#27ae60"/>
            </svg>`,
        };
        return flowers[type] || flowers.chrysanthemum;
    }
}

// ===== 纪念墙 =====
class MemorialWall {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }

    async loadStats(lovedOneId) {
        try {
            const resp = await apiFetch(`/api/memorial-wall/${lovedOneId}`);
            if (resp.ok) {
                const data = await resp.json();
                this.render(data);
            }
        } catch (e) {
            console.error('Failed to load memorial wall:', e);
        }
    }

    render(data) {
        if (!this.container) return;
        this.container.innerHTML = `
            <div class="memorial-stats">
                <div class="stat-item">
                    <div class="stat-icon">🕯️</div>
                    <div class="stat-count">${data.candle_count || 0}</div>
                    <div class="stat-label">蜡烛</div>
                </div>
                <div class="stat-item">
                    <div class="stat-icon">💐</div>
                    <div class="stat-count">${data.flower_count || 0}</div>
                    <div class="stat-label">献花</div>
                </div>
                <div class="stat-item">
                    <div class="stat-icon">🙏</div>
                    <div class="stat-count">${data.prayer_count || 0}</div>
                    <div class="stat-label">祈福</div>
                </div>
            </div>
        `;
    }
}

// CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes flowerAppear {
        from { transform: scale(0) rotate(-180deg); opacity: 0; }
        to { transform: scale(1) rotate(0deg); opacity: 1; }
    }
    @keyframes flowerFade {
        from { opacity: 1; }
        to { opacity: 0; transform: translateY(-20px); }
    }
    .flower-offering {
        position: absolute;
        transition: all 0.3s ease;
    }
    .flower-message {
        font-size: 11px;
        color: rgba(255,255,255,0.7);
        text-align: center;
        margin-top: 4px;
        max-width: 80px;
    }
    .memorial-stats {
        display: flex;
        gap: 24px;
        justify-content: center;
        padding: 16px;
    }
    .stat-item {
        text-align: center;
    }
    .stat-icon {
        font-size: 24px;
        margin-bottom: 4px;
    }
    .stat-count {
        font-size: 20px;
        font-weight: bold;
        color: var(--primary, #efc7a0);
    }
    .stat-label {
        font-size: 12px;
        color: var(--text-muted, rgba(255,244,233,0.7));
    }
`;
document.head.appendChild(style);

// Export
window.CandleSystem = CandleSystem;
window.FlowerSystem = FlowerSystem;
window.MemorialWall = MemorialWall;
