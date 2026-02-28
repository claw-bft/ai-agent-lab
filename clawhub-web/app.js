/**
 * ClawHub Web - 技能包市场前端应用
 * 从注册表API动态获取数据
 */

// API配置
const REGISTRY_API_URL = 'https://claw-bft.github.io/ai-agent-lab/registry/api';

// 全局数据存储
let skillsData = [];
let categoriesData = [];
let isLoading = true;
let loadError = null;

// DOM 元素
let skillsGrid, categoriesGrid, searchInput, searchBtn, filterTags, sortSelect, themeToggle, skillModal, modalClose, modalBody;

// 状态
let currentCategory = 'all';
let currentSort = 'downloads';
let searchQuery = '';

// 初始化
async function init() {
    // 获取DOM元素
    skillsGrid = document.getElementById('skills-grid');
    categoriesGrid = document.getElementById('categories-grid');
    searchInput = document.getElementById('search-input');
    searchBtn = document.getElementById('search-btn');
    filterTags = document.getElementById('filter-tags');
    sortSelect = document.getElementById('sort-select');
    themeToggle = document.getElementById('theme-toggle');
    skillModal = document.getElementById('skill-modal');
    modalClose = document.getElementById('modal-close');
    modalBody = document.getElementById('modal-body');
    
    // 显示加载状态
    showLoading();
    
    // 从API加载数据
    await loadDataFromAPI();
    
    // 设置事件监听
    setupEventListeners();
    
    // 加载主题
    loadTheme();
    
    // 动画统计数字
    animateStats();
}

// 显示加载状态
function showLoading() {
    if (skillsGrid) {
        skillsGrid.innerHTML = `
            <div class="loading-state" style="grid-column: 1 / -1; text-align: center; padding: 60px;">
                <div class="loading-spinner" style="
                    width: 48px;
                    height: 48px;
                    border: 3px solid var(--border);
                    border-top-color: var(--primary);
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 16px;
                "></div>
                <p style="color: var(--text-muted);">正在加载技能包数据...</p>
            </div>
        `;
    }
}

// 从API加载数据
async function loadDataFromAPI() {
    try {
        // 并行加载技能和分类数据
        const [skillsResponse, categoriesResponse] = await Promise.all([
            fetch(`${REGISTRY_API_URL}/skills.json`).catch(() => null),
            fetch(`${REGISTRY_API_URL}/categories.json`).catch(() => null)
        ]);
        
        if (skillsResponse && skillsResponse.ok) {
            const skillsResult = await skillsResponse.json();
            skillsData = skillsResult.skills || [];
            
            // 转换API数据格式为前端格式
            skillsData = skillsData.map(skill => ({
                name: skill.name || skill.id,
                displayName: skill.display_name || skill.name || skill.id,
                version: skill.version || '1.0.0',
                description: skill.description || '',
                icon: skill.icon || getDefaultIcon(skill.category),
                downloads: skill.downloads || 0,
                rating: skill.rating || 0,
                tags: skill.tags || [],
                category: skill.category || 'other',
                author: skill.author || 'claw-bft',
                updated: skill.updated_at || skill.created_at || '2026-02-01',
                coverage: skill.coverage || 'N/A',
                installUrl: skill.install_url || '',
                docsUrl: skill.docs_url || ''
            }));
        } else {
            // API加载失败，使用备用数据
            console.warn('API加载失败，使用备用数据');
            loadFallbackData();
        }
        
        if (categoriesResponse && categoriesResponse.ok) {
            const categoriesResult = await categoriesResponse.json();
            const categoriesMap = categoriesResult.categories || {};
            
            // 转换分类数据格式
            categoriesData = Object.entries(categoriesMap).map(([id, cat]) => ({
                id: id,
                name: cat.name || id,
                icon: cat.icon || getCategoryIcon(id),
                description: cat.description || '',
                count: cat.skills ? cat.skills.length : skillsData.filter(s => s.category === id).length
            }));
        } else {
            // 从技能数据生成分类
            generateCategoriesFromSkills();
        }
        
        isLoading = false;
        renderSkills();
        renderCategories();
        
    } catch (error) {
        console.error('加载数据失败:', error);
        loadError = error.message;
        loadFallbackData();
        isLoading = false;
        renderSkills();
        renderCategories();
    }
}

// 加载备用数据（当API不可用时）
function loadFallbackData() {
    skillsData = [
        {
            name: "finance-pro",
            displayName: "Finance Pro",
            version: "1.2.0",
            description: "多数据源金融数据获取，支持Yahoo/东方财富，含技术指标计算",
            icon: "💰",
            downloads: 342,
            rating: 4.8,
            tags: ["finance", "data"],
            category: "finance",
            author: "claw-bft",
            updated: "2026-02-25"
        },
        {
            name: "stock-portfolio-analyzer",
            displayName: "Stock Portfolio Analyzer",
            version: "1.1.0",
            description: "投资组合分析与早报生成，支持多维度风险评估",
            icon: "📈",
            downloads: 298,
            rating: 4.7,
            tags: ["finance", "analysis"],
            category: "finance",
            author: "claw-bft",
            updated: "2026-02-26"
        },
        {
            name: "coding-pro",
            displayName: "Coding Pro",
            version: "1.0.0",
            description: "AI代码生成器，支持多语言和框架，含测试生成",
            icon: "💻",
            downloads: 256,
            rating: 4.5,
            tags: ["coding", "ai"],
            category: "coding",
            author: "claw-bft",
            updated: "2026-02-20"
        },
        {
            name: "skill-cli",
            displayName: "Skill CLI",
            version: "2.0.0",
            description: "自然语言执行层，让AI理解并执行复杂任务",
            icon: "🎯",
            downloads: 412,
            rating: 4.9,
            tags: ["cli", "core"],
            category: "ai",
            author: "claw-bft",
            updated: "2026-02-27"
        },
        {
            name: "research-pro",
            displayName: "Research Pro",
            version: "1.0.0",
            description: "智能研究助手，文献综述与竞品分析",
            icon: "🔬",
            downloads: 189,
            rating: 4.6,
            tags: ["research", "analysis"],
            category: "research",
            author: "claw-bft",
            updated: "2026-02-22"
        },
        {
            name: "product-pro",
            displayName: "Product Pro",
            version: "1.1.0",
            description: "PRD生成与产品管理，快速产出专业文档",
            icon: "📦",
            downloads: 234,
            rating: 4.7,
            tags: ["product", "docs"],
            category: "product",
            author: "claw-bft",
            updated: "2026-02-24"
        },
        {
            name: "memory-enhanced",
            displayName: "Memory Enhanced",
            version: "1.0.0",
            description: "向量记忆系统，基于sqlite-vec的长期记忆",
            icon: "🧠",
            downloads: 178,
            rating: 4.4,
            tags: ["ai", "memory"],
            category: "ai",
            author: "claw-bft",
            updated: "2026-02-18"
        },
        {
            name: "agent-collaboration",
            displayName: "Agent Collaboration",
            version: "1.0.0",
            description: "ACP协议多智能体协作框架",
            icon: "🤝",
            downloads: 156,
            rating: 4.5,
            tags: ["ai", "collaboration"],
            category: "ai",
            author: "claw-bft",
            updated: "2026-02-19"
        },
        {
            name: "claude-domain-skills",
            displayName: "Claude Domain Skills",
            version: "2.0.0",
            description: "18个领域的专业知识库，涵盖商业/金融/创意等",
            icon: "🎓",
            downloads: 567,
            rating: 4.9,
            tags: ["domains", "knowledge"],
            category: "ai",
            author: "claw-bft",
            updated: "2026-02-28"
        },
        {
            name: "token-manager",
            displayName: "Token Manager",
            version: "1.0.0",
            description: "统一配置管理系统，多技能包配置共享",
            icon: "🔐",
            downloads: 312,
            rating: 4.8,
            tags: ["config", "core"],
            category: "productivity",
            author: "claw-bft",
            updated: "2026-02-23"
        }
    ];
    generateCategoriesFromSkills();
}

// 从技能数据生成分类
function generateCategoriesFromSkills() {
    const categoryMap = {};
    
    skillsData.forEach(skill => {
        const cat = skill.category || 'other';
        if (!categoryMap[cat]) {
            categoryMap[cat] = {
                id: cat,
                name: getCategoryName(cat),
                icon: getCategoryIcon(cat),
                description: getCategoryDescription(cat),
                count: 0
            };
        }
        categoryMap[cat].count++;
    });
    
    categoriesData = Object.values(categoryMap);
}

// 获取分类名称
function getCategoryName(id) {
    const names = {
        finance: '金融分析',
        coding: '开发工具',
        research: '研究分析',
        product: '产品管理',
        ai: 'AI增强',
        productivity: '生产力',
        domains: '领域知识',
        infrastructure: '基础设施',
        ai_enhancement: 'AI增强',
        development: '开发工具',
        other: '其他'
    };
    return names[id] || id;
}

// 获取分类描述
function getCategoryDescription(id) {
    const descriptions = {
        finance: '股票、基金、投资组合分析工具',
        coding: '代码生成、CLI工具、部署助手',
        research: '文献综述、竞品分析、数据研究',
        product: 'PRD生成、需求分析、项目管理',
        ai: '记忆系统、多智能体、工作流',
        productivity: '通知服务、模板工具、效率提升',
        domains: '18个领域的专业知识库',
        infrastructure: '核心框架、配置管理、协议实现',
        ai_enhancement: 'AI增强功能与工具',
        development: '开发与部署工具',
        other: '其他技能包'
    };
    return descriptions[id] || '';
}

// 获取分类图标
function getCategoryIcon(id) {
    const icons = {
        finance: '💰',
        coding: '💻',
        research: '🔬',
        product: '📦',
        ai: '🧠',
        productivity: '⚡',
        domains: '🎓',
        infrastructure: '🏗️',
        ai_enhancement: '🤖',
        development: '🔧',
        other: '📂'
    };
    return icons[id] || '📦';
}

// 获取默认图标
function getDefaultIcon(category) {
    return getCategoryIcon(category);
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
                    <span class="skill-rating">⭐ ${skill.rating ? skill.rating.toFixed(1) : '0.0'}</span>
                    <span class="skill-downloads">📥 ${skill.downloads}</span>
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
    
    const userRating = getUserRating(skillName);
    const ratingData = getRatingDistribution(skillName);
    
    modalBody.innerHTML = `
        <div class="modal-header">
            <div class="modal-icon">${skill.icon}</div>
            <div>
                <h2 class="modal-title">${skill.name}</h2>
                <p class="modal-meta">by ${skill.author} · v${skill.version}</p>
            </div>
        </div>
        <p class="modal-description">${skill.description}</p>
        
        <!-- 评分区域 -->
        <div class="rating-section">
            <div class="rating-summary">
                <div class="rating-big">
                    <span class="rating-score">${skill.rating ? skill.rating.toFixed(1) : '0.0'}</span>
                    <div class="rating-stars-display">${renderStars(skill.rating || 0)}</div>
                    <span class="rating-count">${ratingData ? ratingData.total + ' 个评分' : '暂无评分'}</span>
                </div>
                <div class="rating-user">
                    <div class="rating-user-label">您的评分</div>
                    ${renderInteractiveStars(skillName, userRating)}
                </div>
            </div>
            ${renderRatingDistribution(skillName)}
        </div>
        
        <div class="modal-stats">
            <div class="modal-stat">
                <div class="modal-stat-value">⭐ ${skill.rating ? skill.rating.toFixed(1) : '0.0'}</div>
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

// ==================== 评分系统 ====================

// 获取用户已评分数据（从localStorage）
function getUserRatings() {
    try {
        return JSON.parse(localStorage.getItem('skillRatings') || '{}');
    } catch {
        return {};
    }
}

// 保存用户评分
function saveUserRating(skillName, rating) {
    const ratings = getUserRatings();
    ratings[skillName] = {
        rating: rating,
        timestamp: Date.now()
    };
    localStorage.setItem('skillRatings', JSON.stringify(ratings));
}

// 获取用户评分
function getUserRating(skillName) {
    const ratings = getUserRatings();
    return ratings[skillName]?.rating || 0;
}

// 渲染星级评分（只读）
function renderStars(rating, maxStars = 5) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = maxStars - fullStars - (hasHalfStar ? 1 : 0);
    
    let html = '';
    for (let i = 0; i < fullStars; i++) {
        html += '<span class="star filled">★</span>';
    }
    if (hasHalfStar) {
        html += '<span class="star half">★</span>';
    }
    for (let i = 0; i < emptyStars; i++) {
        html += '<span class="star empty">★</span>';
    }
    return html;
}

// 渲染交互式星级评分
function renderInteractiveStars(skillName, currentRating = 0) {
    let html = '<div class="rating-stars interactive" data-skill="' + skillName + '">';
    for (let i = 1; i <= 5; i++) {
        const filled = i <= currentRating ? 'filled' : 'empty';
        html += `<span class="star ${filled}" data-rating="${i}" onclick="submitRating('${skillName}', ${i})" onmouseover="hoverRating(this, ${i})" onmouseout="resetRating(this, ${currentRating})">★</span>`;
    }
    html += '</div>';
    return html;
}

// 悬停评分效果
function hoverRating(container, rating) {
    const stars = container.parentElement.querySelectorAll('.star');
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('hover');
        } else {
            star.classList.remove('hover');
        }
    });
}

// 重置评分显示
function resetRating(container, currentRating) {
    const stars = container.parentElement.querySelectorAll('.star');
    stars.forEach((star, index) => {
        star.classList.remove('hover');
        if (index < currentRating) {
            star.classList.add('filled');
            star.classList.remove('empty');
        } else {
            star.classList.add('empty');
            star.classList.remove('filled');
        }
    });
}

// 提交评分
function submitRating(skillName, rating) {
    // 保存到本地存储
    saveUserRating(skillName, rating);
    
    // 更新技能数据（模拟）
    const skill = skillsData.find(s => s.name === skillName);
    if (skill) {
        // 模拟更新评分（实际应该发送到后端API）
        const oldRating = skill.rating || 0;
        const oldCount = skill.ratingCount || Math.floor(skill.downloads / 10) || 1;
        const newCount = oldCount + 1;
        skill.rating = ((oldRating * oldCount) + rating) / newCount;
        skill.ratingCount = newCount;
        skill.userRating = rating;
        
        // 刷新显示
        showSkillDetail(skillName);
        renderSkills();
    }
    
    showToast(`已评分: ${rating} ⭐`);
    
    // 模拟发送到后端（实际项目中应该调用API）
    console.log(`[Rating] Skill: ${skillName}, Rating: ${rating}`);
}

// 获取评分分布（模拟数据）
function getRatingDistribution(skillName) {
    // 模拟评分分布数据
    const skill = skillsData.find(s => s.name === skillName);
    if (!skill) return null;
    
    const total = skill.ratingCount || Math.floor(skill.downloads / 10) || 10;
    const avgRating = skill.rating || 4.0;
    
    // 根据平均分生成合理的分布
    const distribution = [0, 0, 0, 0, 0];
    let remaining = total;
    
    // 5星最多，依次递减
    for (let i = 4; i >= 0; i--) {
        const weight = (i + 1) / 15; // 权重因子
        const count = Math.floor(remaining * weight * (avgRating / 3));
        distribution[i] = Math.min(count, remaining);
        remaining -= distribution[i];
    }
    distribution[0] += remaining; // 剩余给1星
    
    return {
        total: total,
        average: avgRating.toFixed(1),
        distribution: distribution.reverse() // 1星到5星
    };
}

// 渲染评分分布条形图
function renderRatingDistribution(skillName) {
    const data = getRatingDistribution(skillName);
    if (!data) return '';
    
    const maxCount = Math.max(...data.distribution);
    
    let html = '<div class="rating-distribution">';
    html += '<div class="rating-distribution-title">评分分布</div>';
    
    for (let i = 5; i >= 1; i--) {
        const count = data.distribution[i - 1];
        const percentage = maxCount > 0 ? (count / data.total * 100).toFixed(0) : 0;
        const barWidth = maxCount > 0 ? (count / maxCount * 100).toFixed(0) : 0;
        
        html += `
            <div class="rating-bar">
                <span class="rating-bar-label">${i}星</span>
                <div class="rating-bar-track">
                    <div class="rating-bar-fill" style="width: ${barWidth}%"></div>
                </div>
                <span class="rating-bar-count">${count}</span>
            </div>
        `;
    }
    
    html += '</div>';
    return html;
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
    const totalSkills = skillsData.length || 24;
    const totalDownloads = skillsData.reduce((sum, s) => sum + (s.downloads || 0), 0);
    const totalCategories = categoriesData.length || 8;
    
    const stats = [
        { id: 'stat-skills', target: totalSkills, suffix: '' },
        { id: 'stat-downloads', target: totalDownloads / 1000, suffix: 'K', decimals: 1 },
        { id: 'stat-categories', target: totalCategories, suffix: '' }
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

// 刷新数据（供外部调用）
async function refreshData() {
    showLoading();
    await loadDataFromAPI();
    renderSkills();
    renderCategories();
    animateStats();
    showToast('数据已刷新');
}

// 导出全局函数
window.showSkillDetail = showSkillDetail;
window.filterByCategory = filterByCategory;
window.copyInstallCommand = copyInstallCommand;
window.refreshData = refreshData;
window.submitRating = submitRating;
window.hoverRating = hoverRating;
window.resetRating = resetRating;

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
    
    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }
`;
document.head.appendChild(style);

// 启动
document.addEventListener('DOMContentLoaded', init);
