/**
 * ClawHub Web - 技能包市场前端应用
 */

// 模拟技能包数据（实际应从API获取）
const skillsData = [
    {
        name: "finance-pro",
        version: "1.2.0",
        description: "多数据源金融数据获取，支持Yahoo/东方财富，含技术指标计算",
        icon: "💰",
        downloads: 342,
        rating: 4.8,
        tags: ["finance", "data"],
        category: "finance",
        author: "AI Agent Lab",
        updated: "2026-02-25"
    },
    {
        name: "stock-portfolio-analyzer",
        version: "1.1.0",
        description: "投资组合分析与早报生成，支持多维度风险评估",
        icon: "📈",
        downloads: 298,
        rating: 4.7,
        tags: ["finance", "analysis"],
        category: "finance",
        author: "AI Agent Lab",
        updated: "2026-02-26"
    },
    {
        name: "coding-pro",
        version: "1.0.0",
        description: "AI代码生成器，支持多语言和框架，含测试生成",
        icon: "💻",
        downloads: 256,
        rating: 4.5,
        tags: ["coding", "ai"],
        category: "coding",
        author: "AI Agent Lab",
        updated: "2026-02-20"
    },
    {
        name: "skill-cli",
        version: "2.0.0",
        description: "自然语言执行层，让AI理解并执行复杂任务",
        icon: "🎯",
        downloads: 412,
        rating: 4.9,
        tags: ["cli", "core"],
        category: "ai",
        author: "AI Agent Lab",
        updated: "2026-02-27"
    },
    {
        name: "research-pro",
        version: "1.0.0",
        description: "智能研究助手，文献综述与竞品分析",
        icon: "🔬",
        downloads: 189,
        rating: 4.6,
        tags: ["research", "analysis"],
        category: "research",
        author: "AI Agent Lab",
        updated: "2026-02-22"
    },
    {
        name: "product-pro",
        version: "1.1.0",
        description: "PRD生成与产品管理，快速产出专业文档",
        icon: "📦",
        downloads: 234,
        rating: 4.7,
        tags: ["product", "docs"],
        category: "product",
        author: "AI Agent Lab",
        updated: "2026-02-24"
    },
    {
        name: "memory-enhanced",
        version: "1.0.0",
        description: "向量记忆系统，基于sqlite-vec的长期记忆",
        icon: "🧠",
        downloads: 178,
        rating: 4.4,
        tags: ["ai", "memory"],
        category: "ai",
        author: "AI Agent Lab",
        updated: "2026-02-18"
    },
    {
        name: "agent-collaboration",
        version: "1.0.0",
        description: "ACP协议多智能体协作框架",
        icon: "🤝",
        downloads: 156,
        rating: 4.5,
        tags: ["ai", "collaboration"],
        category: "ai",
        author: "AI Agent Lab",
        updated: "2026-02-19"
    },
    {
        name: "workflow-orchestrator",
        version: "1.0.0",
        description: "可视化工作流引擎，拖拽式构建AI流程",
        icon: "⚙️",
        downloads: 201,
        rating: 4.6,
        tags: ["workflow", "automation"],
        category: "ai",
        author: "AI Agent Lab",
        updated: "2026-02-21"
    },
    {
        name: "claude-domain-skills",
        version: "2.0.0",
        description: "18个领域的专业知识库，涵盖商业/金融/创意等",
        icon: "🎓",
        downloads: 567,
        rating: 4.9,
        tags: ["domains", "knowledge"],
        category: "ai",
        author: "AI Agent Lab",
        updated: "2026-02-28"
    },
    {
        name: "context-compressor",
        version: "1.0.0",
        description: "上下文压缩与优化，提升长对话效率",
        icon: "🗜️",
        downloads: 145,
        rating: 4.3,
        tags: ["optimization", "ai"],
        category: "ai",
        author: "AI Agent Lab",
        updated: "2026-02-15"
    },
    {
        name: "token-manager",
        version: "1.0.0",
        description: "统一配置管理系统，多技能包配置共享",
        icon: "🔐",
        downloads: 312,
        rating: 4.8,
        tags: ["config", "core"],
        category: "ai",
        author: "AI Agent Lab",
        updated: "2026-02-23"
    }
];

const categoriesData = [
    { id: "finance", name: "金融分析", icon: "💰", description: "股票、基金、投资组合分析工具", count: 3 },
    { id: "coding", name: "开发工具", icon: "💻", description: "代码生成、CLI工具、部署助手", count: 4 },
    { id: "research", name: "研究分析", icon: "🔬", description: "文献综述、竞品分析、数据研究", count: 2 },
    { id: "product", name: "产品管理", icon: "📦", description: "PRD生成、需求分析、项目管理", count: 2 },
    { id: "ai", name: "AI增强", icon: "🧠", description: "记忆系统、多智能体、工作流", count: 8 },
    { id: "productivity", name: "生产力", icon: "⚡", description: "通知服务、模板工具、效率提升", count: 3 },
    { id: "domains", name: "领域知识", icon: "🎓", description: "18个领域的专业知识库", count: 1 },
    { id: "infrastructure", name: "基础设施", icon: "🏗️", description: "核心框架、配置管理、协议实现", count: 4 }
];

// DOM 元素
const skillsGrid = document.getElementById('skills-grid');
const categoriesGrid = document.getElementById('categories-grid');
const searchInput = document.getElementById('search-input');
const searchBtn = document.getElementById('search-btn');
const filterTags = document.getElementById('filter-tags');
const sortSelect = document.getElementById('sort-select');
const themeToggle = document.getElementById('theme-toggle');
const skillModal = document.getElementById('skill-modal');
const modalClose = document.getElementById('modal-close');
const modalBody = document.getElementById('modal-body');

// 状态
let currentCategory = 'all';
let currentSort = 'downloads';
let searchQuery = '';

// 初始化
function init() {
    renderSkills();
    renderCategories();
    setupEventListeners();
    loadTheme();
    animateStats();
}

// 渲染技能包列表
function renderSkills() {
    let filtered = skillsData;
    
    // 分类筛选
    if (currentCategory !== 'all') {
        filtered = filtered.filter(s => s.category === currentCategory || s.tags.includes(currentCategory));
    }
    
    // 搜索筛选
    if (searchQuery) {
        const q = searchQuery.toLowerCase();
        filtered = filtered.filter(s => 
            s.name.toLowerCase().includes(q) ||
            s.description.toLowerCase().includes(q) ||
            s.tags.some(t => t.toLowerCase().includes(q))
        );
    }
    
    // 排序
    filtered.sort((a, b) => {
        if (currentSort === 'downloads') return b.downloads - a.downloads;
        if (currentSort === 'rating') return b.rating - a.rating;
        if (currentSort === 'updated') return new Date(b.updated) - new Date(a.updated);
        return 0;
    });
    
    if (filtered.length === 0) {
        skillsGrid.innerHTML = `
            <div class="empty-state" style="grid-column: 1 / -1;">
                <div class="empty-state-icon">🔍</div>
                <p>没有找到匹配的技能包</p>
            </div>
        `;
        return;
    }
    
    skillsGrid.innerHTML = filtered.map(skill => `
        <div class="skill-card" onclick="showSkillDetail('${skill.name}')">
            <div class="skill-header">
                <div class="skill-icon">${skill.icon}</div>
                <div class="skill-meta">
                    <div class="skill-name">${skill.name}</div>
                    <span class="skill-version">v${skill.version}</span>
                </div>
            </div>
            <p class="skill-description">${skill.description}</p>
            <div class="skill-footer">
                <div class="skill-stats">
                    <span>⭐ ${skill.rating}</span>
                    <span>📥 ${skill.downloads}</span>
                </div>
                <div class="skill-tags">
                    ${skill.tags.slice(0, 2).map(t => `<span class="skill-tag">${t}</span>`).join('')}
                </div>
            </div>
        </div>
    `).join('');
}

// 渲染分类
function renderCategories() {
    categoriesGrid.innerHTML = categoriesData.map(cat => `
        <div class="category-card" onclick="filterByCategory('${cat.id}')">
            <div class="category-icon">${cat.icon}</div>
            <h3 class="category-name">${cat.name}</h3>
            <p class="category-description">${cat.description}</p>
            <span class="category-count">${cat.count} 个技能包</span>
        </div>
    `).join('');
}

// 按分类筛选
function filterByCategory(category) {
    currentCategory = category;
    
    // 更新标签状态
    document.querySelectorAll('.tag').forEach(tag => {
        tag.classList.toggle('active', tag.dataset.category === category);
    });
    
    // 滚动到技能区域
    document.getElementById('skills').scrollIntoView({ behavior: 'smooth' });
    
    renderSkills();
}

// 显示技能详情
function showSkillDetail(skillName) {
    const skill = skillsData.find(s => s.name === skillName);
    if (!skill) return;
    
    modalBody.innerHTML = `
        <div class="modal-header">
            <div class="modal-icon">${skill.icon}</div>
            <div>
                <h2 class="modal-title">${skill.name}</h2>
                <p class="modal-meta">by ${skill.author} · v${skill.version}</p>
            </div>
        </div>
        <p class="modal-description">${skill.description}</p>
        <div class="modal-stats">
            <div class="modal-stat">
                <div class="modal-stat-value">⭐ ${skill.rating}</div>
                <div class="modal-stat-label">评分</div>
            </div>
            <div class="modal-stat">
                <div class="modal-stat-value">📥 ${skill.downloads}</div>
                <div class="modal-stat-label">下载</div>
            </div>
            <div class="modal-stat">
                <div class="modal-stat-value">${skill.tags.length}</div>
                <div class="modal-stat-label">标签</div>
            </div>
        </div>
        <div class="modal-install">
            <div class="modal-install-label">安装命令</div>
            <code class="modal-install-code">claw install ${skill.name}</code>
        </div>
        <div class="modal-actions">
            <button class="btn btn-primary" onclick="copyInstallCommand('${skill.name}')">
                📋 复制命令
            </button>
            <a href="https://github.com/claw-bft/ai-agent-lab/tree/main/${skill.name}" 
               class="btn btn-secondary" target="_blank">
                查看源码
            </a>
        </div>
    `;
    
    skillModal.classList.add('active');
}

// 复制安装命令
function copyInstallCommand(skillName) {
    navigator.clipboard.writeText(`claw install ${skillName}`);
    showToast('已复制到剪贴板');
}

// 显示提示
function showToast(message) {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        bottom: 24px;
        left: 50%;
        transform: translateX(-50%);
        background: var(--primary);
        color: white;
        padding: 12px 24px;
        border-radius: var(--radius-sm);
        font-size: 0.875rem;
        z-index: 300;
        animation: fadeInUp 0.3s ease;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 2000);
}

// 设置事件监听
function setupEventListeners() {
    // 搜索
    searchBtn.addEventListener('click', () => {
        searchQuery = searchInput.value.trim();
        renderSkills();
    });
    
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchQuery = searchInput.value.trim();
            renderSkills();
        }
    });
    
    // 分类标签
    filterTags.addEventListener('click', (e) => {
        if (e.target.classList.contains('tag')) {
            document.querySelectorAll('.tag').forEach(t => t.classList.remove('active'));
            e.target.classList.add('active');
            currentCategory = e.target.dataset.category;
            renderSkills();
        }
    });
    
    // 排序
    sortSelect.addEventListener('change', (e) => {
        currentSort = e.target.value;
        renderSkills();
    });
    
    // 主题切换
    themeToggle.addEventListener('click', toggleTheme);
    
    // 模态框关闭
    modalClose.addEventListener('click', () => {
        skillModal.classList.remove('active');
    });
    
    skillModal.addEventListener('click', (e) => {
        if (e.target === skillModal) {
            skillModal.classList.remove('active');
        }
    });
    
    // ESC关闭模态框
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            skillModal.classList.remove('active');
        }
    });
}

// 主题切换
function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    themeToggle.textContent = next === 'light' ? '🌙' : '☀️';
}

// 加载主题
function loadTheme() {
    const saved = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
    themeToggle.textContent = saved === 'light' ? '🌙' : '☀️';
}

// 动画统计数字
function animateStats() {
    const stats = [
        { id: 'stat-skills', target: 24, suffix: '' },
        { id: 'stat-downloads', target: 1.2, suffix: 'K', decimals: 1 },
        { id: 'stat-categories', target: 8, suffix: '' }
    ];
    
    stats.forEach(({ id, target, suffix, decimals = 0 }) => {
        const el = document.getElementById(id);
        if (!el) return;
        
        let current = 0;
        const increment = target / 30;
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            el.textContent = current.toFixed(decimals) + suffix;
        }, 50);
    });
}

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translate(-50%, 20px);
        }
        to {
            opacity: 1;
            transform: translate(-50%, 0);
        }
    }
    
    @keyframes fadeOut {
        from {
            opacity: 1;
        }
        to {
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// 启动
document.addEventListener('DOMContentLoaded', init);

// 导出全局函数
window.showSkillDetail = showSkillDetail;
window.filterByCategory = filterByCategory;
window.copyInstallCommand = copyInstallCommand;
