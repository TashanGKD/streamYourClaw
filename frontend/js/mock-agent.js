/**
 * Mock Agent 模拟器
 * 模拟 openclaw agent 的工作流程
 */

class MockAgent {
    constructor(statusManager, thoughtLogger, mindmapRenderer) {
        this.statusManager = statusManager;
        this.videoStatusManager = window.videoStatusManager || null;
        this.thoughtLogger = thoughtLogger;
        this.mindmapRenderer = mindmapRenderer;
        
        this.isRunning = false;
        this.taskCounter = 0;
        
        // 模拟任务库
        this.taskTemplates = [
            {
                name: '数据分析',
                steps: [
                    { type: 'thinking', message: '分析数据结构...' },
                    { type: 'waiting', message: '等待数据加载...' },
                    { type: 'thinking', message: '处理数据格式...' },
                    { type: 'success', message: '数据分析完成' }
                ]
            },
            {
                name: '代码生成',
                steps: [
                    { type: 'thinking', message: '理解需求...' },
                    { type: 'typing', message: '编写代码框架...' },
                    { type: 'waiting', message: '等待依赖安装...' },
                    { type: 'thinking', message: '优化代码结构...' },
                    { type: 'success', message: '代码生成完成' }
                ]
            },
            {
                name: '文档编写',
                steps: [
                    { type: 'thinking', message: '整理文档结构...' },
                    { type: 'typing', message: '编写文档内容...' },
                    { type: 'waiting', message: '等待资料检索...' },
                    { type: 'thinking', message: '润色文档...' },
                    { type: 'success', message: '文档编写完成' }
                ]
            },
            {
                name: '问题调试',
                steps: [
                    { type: 'thinking', message: '分析错误日志...' },
                    { type: 'waiting', message: '等待复现结果...' },
                    { type: 'thinking', message: '定位问题根源...' },
                    { type: 'typing', message: '修复代码...' },
                    { type: 'success', message: '问题已解决' }
                ]
            }
        ];
    }

    /**
     * 开始模拟
     */
    start() {
        if (this.isRunning) {
            console.warn('[MockAgent] 已经在运行中');
            return;
        }
        
        this.isRunning = true;
        console.log('[MockAgent] 开始模拟');
        
        // 延迟 2 秒后开始第一个任务
        setTimeout(() => {
            this.runTaskCycle();
        }, 2000);
    }

    /**
     * 停止模拟
     */
    stop() {
        this.isRunning = false;
        console.log('[MockAgent] 停止模拟');
    }

    /**
     * 运行任务周期
     */
    async runTaskCycle() {
        while (this.isRunning) {
            // 选择随机任务
            const taskIndex = Math.floor(Math.random() * this.taskTemplates.length);
            const task = this.taskTemplates[taskIndex];
            
            this.taskCounter++;
            const taskName = `${task.name} #${this.taskCounter}`;
            
            // 执行任务
            await this.executeTask(taskName, task.steps);
            
            // 任务间休息 3-8 秒
            const restTime = 3000 + Math.random() * 5000;
            await this.sleep(restTime);
        }
    }

    /**
     * 执行单个任务
     * @param {string} taskName 
     * @param {Array} steps 
     */
    async executeTask(taskName, steps) {
        // Demo 模式下不干扰视频播放
        const isDemoMode = this.videoStatusManager && this.videoStatusManager.demoMode;
        
        // 1. 接收任务（typing 状态）
        this.statusManager.setStatus('typing');
        if (!isDemoMode && this.videoStatusManager) {
            this.videoStatusManager.setStatus('typing');
        }
        this.thoughtLogger.addLog(`📥 收到新任务：${taskName}`, 'info');
        
        await this.sleep(1500 + Math.random() * 1000);
        
        // 2. 执行任务步骤
        for (const step of steps) {
            if (!this.isRunning) break;
            
            // 根据步骤类型设置状态
            if (step.type === 'typing') {
                this.statusManager.setStatus('typing');
                if (!isDemoMode && this.videoStatusManager) {
                    this.videoStatusManager.setStatus('typing');
                }
            } else if (step.type === 'waiting') {
                this.statusManager.setStatus('waiting');
                if (!isDemoMode && this.videoStatusManager) {
                    this.videoStatusManager.setStatus('waiting');
                }
            } else if (step.type === 'thinking') {
                this.statusManager.setStatus('thinking');
                if (!isDemoMode && this.videoStatusManager) {
                    this.videoStatusManager.setStatus('thinking');
                }
            }
            
            // 添加日志
            this.thoughtLogger.addLog(step.message, step.type);
            
            // 模拟步骤执行时间
            const stepDuration = 1000 + Math.random() * 2000;
            await this.sleep(stepDuration);
        }
        
        // 3. 任务完成
        this.statusManager.setStatus('thinking');
        if (!isDemoMode && this.videoStatusManager) {
            this.videoStatusManager.setStatus('thinking');
        }
        this.thoughtLogger.addLog(`✅ 任务完成：${taskName}`, 'success');
        
        // 更新思维导图（可选）
        this.updateMindmap(taskName);
    }

    /**
     * 更新思维导图
     * @param {string} taskName 
     */
    updateMindmap(taskName) {
        // 这里可以触发思维导图的更新
        // 简单示例：刷新数据
        if (this.mindmapRenderer) {
            // 实际使用时可以动态添加节点
            console.log('[MockAgent] 任务完成，可更新思维导图:', taskName);
        }
    }

    /**
     * 延迟函数
     * @param {number} ms - 毫秒
     * @returns {Promise}
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * 手动添加任务
     * @param {string} taskName 
     * @param {Array} steps 
     */
    addTask(taskName, steps) {
        this.taskTemplates.push({
            name: taskName,
            steps: steps
        });
    }
}

// 导出为全局变量
window.MockAgent = MockAgent;
