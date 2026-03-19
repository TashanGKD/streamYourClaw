/**
 * 视频状态管理器
 * 根据工作状态管理和播放对应的视频
 */

class VideoStatusManager {
    constructor() {
        this.currentStatus = 'thinking';
        this.config = null;
        this.videoElement = null;
        this.fallbackElement = null;
        this.currentVideoIndex = 0;
        this.loadedVideos = new Map();
        
        // Demo 模式：内部状态机
        this.demoMode = true;
        this.demoStateIndex = 0;
        this.demoStates = ['typing', 'waiting', 'thinking'];
        this.demoTimer = null;
        this.demoInterval = 5000; // 默认 5 秒，但会根据视频时长调整
        
        this.init();
    }

    async init() {
        // 获取 DOM 元素
        this.videoElement = document.getElementById('crab-status-video');
        this.fallbackElement = document.getElementById('crab-status-fallback');
        
        if (!this.videoElement) {
            console.error('[VideoStatusManager] 视频元素未找到');
            return;
        }

        // 加载配置文件
        await this.loadConfig();
        
        // 绑定事件
        this.bindEvents();
        
        // 播放初始状态
        this.playStatus('thinking');
        
        // 启动 Demo 模式（不自动切换，等待视频结束）
        if (this.demoMode) {
            console.log('[VideoStatusManager] Demo 模式已启动，等待视频播放完成');
        }
        
        console.log('[VideoStatusManager] 初始化完成');
    }

    /**
     * 加载配置文件
     */
    async loadConfig() {
        try {
            const response = await fetch('assets/videos/meta.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            this.config = await response.json();
            console.log('[VideoStatusManager] 配置加载成功');
        } catch (error) {
            console.error('[VideoStatusManager] 配置加载失败:', error);
            // 使用默认配置
            this.config = this.getDefaultConfig();
        }
    }

    /**
     * 获取默认配置
     */
    getDefaultConfig() {
        return {
            states: {
                typing: {
                    name: '输入中',
                    videos: [{ file: 'typing-01.mp4', duration: 3000, weight: 1.0 }],
                    indicatorColor: '#58a6ff'
                },
                waiting: {
                    name: '等待中',
                    videos: [{ file: 'waiting-01.mp4', duration: 4000, weight: 1.0 }],
                    indicatorColor: '#a371f7'
                },
                thinking: {
                    name: '思考中',
                    videos: [{ file: 'thinking-01.mp4', duration: 3500, weight: 1.0 }],
                    indicatorColor: '#d29922'
                }
            },
            settings: {
                autoPlay: true,
                loop: true,
                muted: true,
                playsInline: true,
                preload: 'auto',
                randomizeOnStateChange: true,
                crossfadeDuration: 300,
                defaultDuration: 3000
            },
            videoConfig: {
                preferredFormat: 'mp4',
                fallbackFormat: 'webm',
                maxRetries: 3,
                retryDelay: 500
            }
        };
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 视频加载完成
        this.videoElement.addEventListener('loadeddata', () => {
            console.log('[VideoStatusManager] 视频加载完成');
            this.videoElement.play().catch(err => {
                console.warn('[VideoStatusManager] 自动播放失败:', err);
                // 不切换到 fallback，因为视频已加载只是播放失败
            });
        });

        // 视频加载错误
        this.videoElement.addEventListener('error', (e) => {
            console.error('[VideoStatusManager] 视频加载错误:', e);
            const stateConfig = this.config.states[this.currentStatus];
            const emoji = stateConfig?.fallback || '💭';
            this.useFallback(emoji);
        });

        // 视频播放结束（用于 Demo 模式切换状态）
        let loopCount = 0;
        const maxLoops = 2; // 每个视频循环 2 次后切换状态
        
        this.videoElement.addEventListener('ended', () => {
            loopCount++;
            
            // Demo 模式下，循环指定次数后切换状态
            if (this.demoMode && loopCount >= maxLoops) {
                loopCount = 0;
                setTimeout(() => {
                    this.cycleDemoState();
                }, 500);
            }
        });
    }

    /**
     * 播放指定状态的视频
     * @param {string} status - 'typing' | 'waiting' | 'thinking'
     */
    async playStatus(status) {
        if (!this.config) {
            console.error('[VideoStatusManager] 配置未加载');
            return;
        }

        const stateConfig = this.config.states[status];
        if (!stateConfig) {
            console.error('[VideoStatusManager] 未知状态:', status);
            return;
        }

        console.log(`[VideoStatusManager] 切换状态：${this.currentStatus} -> ${status}`);
        this.currentStatus = status;

        // 更新状态指示器颜色和文字
        this.updateIndicatorColor(stateConfig);

        // 随机选择视频
        const videoInfo = this.selectRandomVideo(stateConfig.videos);
        
        // 加载并播放视频（传入 emoji 作为降级方案）
        await this.loadAndPlayVideo(videoInfo, stateConfig.fallback);
    }

    /**
     * 更新状态指示器颜色和文字
     * @param {Object} stateConfig 
     */
    updateIndicatorColor(stateConfig) {
        // 更新所有指示器点的颜色
        const allDots = document.querySelectorAll('.indicator-dot');
        allDots.forEach(dot => {
            dot.style.backgroundColor = ''; // 清空内联样式，使用 CSS 类
        });
        
        // 设置当前状态的指示器点颜色
        const currentDot = document.querySelector(`.indicator-dot.${this.currentStatus}`);
        if (currentDot) {
            currentDot.style.backgroundColor = stateConfig.indicatorColor;
        }
        
        // 更新指示器文字
        const indicatorText = document.querySelector('.indicator-text');
        if (indicatorText && stateConfig.name) {
            indicatorText.textContent = stateConfig.name;
        }
    }

    /**
     * 随机选择视频（根据权重）
     * @param {Array} videos 
     * @returns {Object}
     */
    selectRandomVideo(videos) {
        if (videos.length === 1) {
            return videos[0];
        }

        // 加权随机选择
        const totalWeight = videos.reduce((sum, v) => sum + v.weight, 0);
        let random = Math.random() * totalWeight;
        
        for (const video of videos) {
            random -= video.weight;
            if (random <= 0) {
                return video;
            }
        }
        
        return videos[0];
    }

    /**
     * 加载并播放视频
     * @param {Object} videoInfo 
     * @param {string} fallbackEmoji 
     */
    async loadAndPlayVideo(videoInfo, fallbackEmoji) {
        const settings = this.config.settings;
        const videoConfig = this.config.videoConfig;
        
        // 设置视频源
        const videoPath = `assets/videos/${videoInfo.file}`;
        
        // 检查视频文件是否存在
        try {
            const response = await fetch(videoPath, { method: 'HEAD' });
            if (!response.ok) {
                throw new Error(`Video not found: ${videoPath}`);
            }
            
            // 视频存在，加载并播放
            this.videoElement.src = videoPath;
            this.videoElement.autoplay = settings.autoPlay;
            this.videoElement.loop = settings.loop;
            this.videoElement.muted = settings.muted;
            this.videoElement.playsInline = settings.playsInline;
            
            if (settings.preload === 'auto') {
                this.videoElement.load();
            }
            
            // 显示视频，隐藏降级方案
            this.videoElement.style.display = 'block';
            if (this.fallbackElement) {
                this.fallbackElement.style.display = 'none';
            }
            
            console.log(`[VideoStatusManager] 加载视频：${videoPath}`);
        } catch (error) {
            console.warn(`[VideoStatusManager] 视频文件不存在，使用降级方案：${videoPath}`);
            this.useFallback(fallbackEmoji || '💭');
        }
    }

    /**
     * 使用降级方案（Emoji 动画）
     * @param {string} emoji 
     */
    useFallback(emoji) {
        console.log('[VideoStatusManager] 使用降级方案：Emoji', emoji);
        
        if (this.videoElement) {
            this.videoElement.style.display = 'none';
        }
        
        if (this.fallbackElement) {
            this.fallbackElement.style.display = 'block';
            const emojiIcon = document.getElementById('emoji-icon');
            if (emojiIcon) {
                emojiIcon.textContent = emoji;
            }
        }
    }

    /**
     * 获取当前状态
     * @returns {string}
     */
    getStatus() {
        return this.currentStatus;
    }

    /**
     * 设置状态（外部调用接口）
     * @param {string} status 
     */
    setStatus(status) {
        this.playStatus(status);
    }

    /**
     * 暂停播放
     */
    pause() {
        if (this.videoElement) {
            this.videoElement.pause();
        }
    }

    /**
     * 恢复播放
     */
    resume() {
        if (this.videoElement) {
            this.videoElement.play();
        }
    }

    /**
     * 重新加载当前状态的视频
     */
    reload() {
        this.playStatus(this.currentStatus);
    }

    /**
     * 启动 Demo 模式
     */
    startDemoMode() {
        console.log('[VideoStatusManager] 启动 Demo 模式，视频播放完成后自动切换');
        
        // Demo 模式不再使用定时器，而是等待视频播放完成
        // cycleDemoState 会在 video ended 事件中调用
    }

    /**
     * 循环切换 Demo 状态
     */
    cycleDemoState() {
        // 获取下一个状态
        this.demoStateIndex = (this.demoStateIndex + 1) % this.demoStates.length;
        const nextStatus = this.demoStates[this.demoStateIndex];
        
        console.log(`[Demo Mode] 视频播放完成，切换状态：${this.currentStatus} -> ${nextStatus}`);
        
        // 播放新状态的视频
        this.playStatus(nextStatus);
    }

    /**
     * 停止 Demo 模式
     */
    stopDemoMode() {
        console.log('[VideoStatusManager] Demo 模式已停止');
    }

    /**
     * 设置 Demo 模式
     * @param {boolean} enabled 
     */
    setDemoMode(enabled) {
        this.demoMode = enabled;
        if (enabled) {
            this.startDemoMode();
        } else {
            this.stopDemoMode();
        }
    }
}

// 导出为全局变量
window.VideoStatusManager = VideoStatusManager;
