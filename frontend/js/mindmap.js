/**
 * 思维导图渲染器
 * 使用 Mermaid.js 渲染任务思维导图
 */

class MindmapRenderer {
    constructor(containerId, dataPath = 'data/mindmap.json') {
        this.container = document.getElementById(containerId);
        this.dataPath = dataPath;
        this.currentData = null;
        this.pollInterval = 2000; // 2 秒轮询一次
        this.pollTimer = null;
        
        if (!this.container) {
            console.error('Mindmap container not found:', containerId);
            return;
        }
        
        this.init();
    }

    async init() {
        // 初始化 Mermaid
        mermaid.initialize({
            startOnLoad: false,
            theme: 'base',
            themeVariables: {
                primaryColor: '#21262d',
                primaryTextColor: '#c9d1d9',
                primaryBorderColor: '#30363d',
                lineColor: '#30363d',
                secondaryColor: '#161b22',
                tertiaryColor: '#0d1117'
            },
            flowchart: {
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }
        });
        
        // 加载初始数据
        await this.loadData();
        
        // 开始轮询
        this.startPolling();
    }

    /**
     * 加载思维导图数据
     */
    async loadData() {
        try {
            const response = await fetch(this.dataPath);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            // 检查数据是否变化
            if (JSON.stringify(data) !== JSON.stringify(this.currentData)) {
                this.currentData = data;
                this.render(data);
            }
        } catch (error) {
            console.error('Failed to load mindmap data:', error);
            this.showError('加载思维导图失败');
        }
    }

    /**
     * 渲染思维导图
     * @param {object} data - 思维导图数据
     */
    render(data) {
        const mermaidCode = this.convertToMermaid(data);
        
        this.container.innerHTML = `
            <div class="mermaid">
                ${mermaidCode}
            </div>
        `;
        
        // 重新渲染 Mermaid
        mermaid.init(undefined, this.container.querySelectorAll('.mermaid'));
        
        console.log('[MindmapRenderer] 思维导图已渲染');
    }

    /**
     * 将 JSON 数据转换为 Mermaid 语法
     * @param {object} data 
     * @returns {string}
     */
    convertToMermaid(data) {
        let mermaid = 'graph TD\n';
        
        // 定义节点样式
        mermaid += '  classDef completed fill:#21262d,stroke:#3fb950,stroke-width:2px,color:#c9d1d9\n';
        mermaid += '  classDef processing fill:#21262d,stroke:#58a6ff,stroke-width:2px,color:#c9d1d9\n';
        mermaid += '  classDef pending fill:#21262d,stroke:#484f58,stroke-width:2px,color:#8b949e\n';
        mermaid += '  classDef root fill:#21262d,stroke:#a371f7,stroke-width:3px,color:#c9d1d9\n';
        
        const nodes = [];
        const edges = [];
        
        // 递归遍历任务树
        const traverse = (task, parentId = null) => {
            const nodeId = `T${task.id.replace(/-/g, '_')}`;
            const label = task.title;
            const status = task.status || 'pending';
            
            nodes.push({
                id: nodeId,
                label: label,
                status: status,
                isRoot: !parentId
            });
            
            if (parentId) {
                edges.push({
                    from: parentId,
                    to: nodeId
                });
            }
            
            if (task.children && task.children.length > 0) {
                task.children.forEach(child => {
                    traverse(child, nodeId);
                });
            }
        };
        
        // 遍历根任务
        if (data.root) {
            data.root.forEach(task => {
                traverse(task);
            });
        }
        
        // 生成 Mermaid 节点定义
        nodes.forEach(node => {
            const shape = node.isRoot ? '[📌 ' : '  [';
            const shapeEnd = node.isRoot ? ']' : ']';
            const label = node.isRoot ? node.label.replace('📌 ', '') : node.label;
            mermaid += `  ${node.id}${shape}${label}${shapeEnd}\n`;
            mermaid += `  class ${node.id} ${node.status}${node.isRoot ? ',root' : ''}\n`;
        });
        
        // 生成 Mermaid 边定义
        edges.forEach(edge => {
            mermaid += `  ${edge.from} --> ${edge.to}\n`;
        });
        
        return mermaid;
    }

    /**
     * 显示错误信息
     * @param {string} message 
     */
    showError(message) {
        this.container.innerHTML = `
            <div class="mindmap-error">
                <span class="icon">⚠️</span>
                <p>${message}</p>
            </div>
        `;
    }

    /**
     * 显示加载状态
     */
    showLoading() {
        this.container.innerHTML = `
            <div class="mindmap-loading">
                <div class="loading-spinner"></div>
                <p>加载思维导图中...</p>
            </div>
        `;
    }

    /**
     * 开始轮询数据
     */
    startPolling() {
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
        }
        
        this.pollTimer = setInterval(() => {
            this.loadData();
        }, this.pollInterval);
        
        console.log('[MindmapRenderer] 开始轮询数据');
    }

    /**
     * 停止轮询
     */
    stopPolling() {
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
            this.pollTimer = null;
        }
    }

    /**
     * 设置轮询间隔
     * @param {number} interval - 毫秒
     */
    setPollInterval(interval) {
        this.pollInterval = interval;
        if (this.pollTimer) {
            this.startPolling();
        }
    }

    /**
     * 手动刷新数据
     */
    async refresh() {
        await this.loadData();
    }
}

// 导出为全局变量
window.MindmapRenderer = MindmapRenderer;
