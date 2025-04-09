class IPCVisualizer {
    constructor() {
        // --- Cache DOM Elements ---
        this.canvas = document.getElementById('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.startBtn = document.getElementById('startBtn');
        this.resetBtn = document.getElementById('resetBtn');
        this.ipcTypeSelect = document.getElementById('ipcType');
        this.sourceProcessSelect = document.getElementById('sourceProcess');
        this.targetProcessSelect = document.getElementById('targetProcess');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.logContent = document.getElementById('logContent'); // The div where log messages go

        // --- State Variables ---
        this.processes = [];
        this.connections = [];
        this.dataPackets = [];
        this.isSimulating = false;
        this.currentIPCType = this.ipcTypeSelect.value; // Initialize from dropdown
        this.animationFrameId = null; // To store the requestAnimationFrame ID

        // --- Setup ---
        this.setupEventListeners();
        this.initializeSimulation(); // Initial setup
    }

    // --- Setup ---

    setupEventListeners() {
        this.startBtn.addEventListener('click', () => this.toggleSimulation());
        this.resetBtn.addEventListener('click', () => this.reset());
        this.ipcTypeSelect.addEventListener('change', (e) => {
            this.currentIPCType = e.target.value;
            this.log(`IPC type changed to: ${this.getIPCTypeName(this.currentIPCType)}`);
            this.reset(); // Reset simulation when IPC type changes
        });
        this.sendBtn.addEventListener('click', () => this.queueMessageToSend());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.queueMessageToSend();
            }
        });

        // Optional: Prevent sending message from/to the same process
        this.sourceProcessSelect.addEventListener('change', () => this.updateTargetProcessOptions());
        this.targetProcessSelect.addEventListener('change', () => this.updateSourceProcessOptions());
        // Initial population of target options based on source
        this.updateTargetProcessOptions();
    }

    initializeSimulation() {
        this.processes = [
            // Centered vertically, spaced horizontally
            { id: 1, x: this.canvas.width * 0.2, y: this.canvas.height / 2, name: 'Process 1', radius: 35 },
            { id: 2, x: this.canvas.width * 0.8, y: this.canvas.height / 2, name: 'Process 2', radius: 35 }
            // Add more processes here if needed
        ];

        // Clear existing connections before creating new ones
        this.connections = [];

        // Create connections based on processes (e.g., all-to-all or specific)
        // For simplicity, let's assume bidirectional capability visualized by one line
        if (this.processes.length >= 2) {
            this.connections.push({
                type: this.currentIPCType, // Store type for potential future logic/styling
                processA: this.processes[0], // Use generic names
                processB: this.processes[1]
            });
        }
        // Add more connections if more processes exist

        this.log(`Initialized with ${this.getIPCTypeName(this.currentIPCType)} mechanism.`);
        this.draw(); // Draw initial state
    }

    // --- Simulation Control ---

    toggleSimulation() {
        this.isSimulating = !this.isSimulating;
        if (this.isSimulating) {
            this.startBtn.textContent = 'Stop Simulation';
            this.log('Simulation started.');
            // Disable changing IPC type while running? Optional.
            // this.ipcTypeSelect.disabled = true;
            this.animationLoop(); // Start the loop
        } else {
            this.startBtn.textContent = 'Start Simulation';
            this.log('Simulation stopped.');
            // Re-enable IPC type changing
            // this.ipcTypeSelect.disabled = false;
            if (this.animationFrameId) {
                cancelAnimationFrame(this.animationFrameId);
                this.animationFrameId = null;
            }
            // Note: Stopping doesn't automatically reset packets in this version
        }
    }

    reset() {
        this.isSimulating = false;
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
            this.animationFrameId = null;
        }
        this.startBtn.textContent = 'Start Simulation';
        this.ipcTypeSelect.disabled = false; // Ensure enabled
        this.dataPackets = []; // Clear packets
        this.logContent.innerHTML = ''; // Clear visual log
        this.messageInput.value = ''; // Clear message input
        this.log('Simulation reset.');
        this.initializeSimulation(); // Re-initialize processes and connections
        // No need to call draw() separately, initializeSimulation calls it.
    }

    // --- Message Handling ---

    queueMessageToSend() {
        if (!this.isSimulating) {
             this.log("Cannot send message: Simulation not started.", "error");
             // Optionally, briefly highlight the start button
             this.startBtn.style.boxShadow = '0 0 5px 2px red';
             setTimeout(() => { this.startBtn.style.boxShadow = ''; }, 1000);
             return;
        }

        const message = this.messageInput.value.trim();
        const sourceId = parseInt(this.sourceProcessSelect.value);
        const targetId = parseInt(this.targetProcessSelect.value);

        if (!message) {
             this.log("Cannot send: Message is empty.", "warn");
             this.messageInput.focus();
             return;
        }
        if (sourceId === targetId) {
             this.log("Cannot send: Source and Target processes cannot be the same.", "warn");
             return;
        }

        const sourceProcess = this.processes.find(p => p.id === sourceId);
        const targetProcess = this.processes.find(p => p.id === targetId);

        if (!sourceProcess || !targetProcess) {
            // This shouldn't happen with the dropdowns, but good practice
            this.log(`Error: Invalid process ID selected.`, "error");
            return;
        }

        // Create a new data packet
        const packet = {
            id: Date.now() + Math.random(), // Unique ID for the packet
            x: sourceProcess.x,
            y: sourceProcess.y,
            startX: sourceProcess.x,
            startY: sourceProcess.y,
            targetX: targetProcess.x,
            targetY: targetProcess.y,
            progress: 0, // 0 to 1
            speed: 0.015, // Controls how fast the packet moves (adjust as needed)
            message: message,
            source: sourceProcess,
            target: targetProcess,
            ipcType: this.currentIPCType, // Store the type used for this packet
            received: false // Flag to prevent duplicate logging
        };
        this.dataPackets.push(packet);

        this.log(`Process ${sourceProcess.id} sending "${message}" to Process ${targetProcess.id} via ${this.getIPCTypeName(this.currentIPCType)}.`);
        this.messageInput.value = ''; // Clear input after queuing
        this.messageInput.focus(); // Keep focus on input
    }

    // --- Animation and Drawing ---

    animationLoop() {
        if (!this.isSimulating) {
            this.animationFrameId = null;
            return; // Stop the loop if simulation is stopped
        }

        // Update state (move packets)
        this.updatePackets();

        // Draw current state
        this.draw();

        // Request next frame
        this.animationFrameId = requestAnimationFrame(this.animationLoop.bind(this));
    }

    updatePackets() {
        const packetsToRemove = [];

        this.dataPackets.forEach((packet, index) => {
            if (packet.received) {
                 // Optionally fade out or keep for a moment before removing
                 // For now, let's mark for immediate removal after logging
                 packetsToRemove.push(index);
                 return;
            }

            packet.progress += packet.speed;
            packet.x = packet.startX + (packet.targetX - packet.startX) * packet.progress;
            packet.y = packet.startY + (packet.targetY - packet.startY) * packet.progress;

            // Check for arrival
            if (packet.progress >= 1) {
                packet.progress = 1; // Cap progress
                packet.x = packet.targetX; // Snap to target
                packet.y = packet.targetY;
                packet.received = true; // Mark as received
                this.log(`Process ${packet.target.id} received "${packet.message}" from Process ${packet.source.id}.`);
                // Trigger visual feedback on the target process? (e.g., brief highlight)
                 this.flashProcess(packet.target.id);
            }
        });

         // Remove received packets (iterate backwards to avoid index issues)
        for (let i = packetsToRemove.length - 1; i >= 0; i--) {
            this.dataPackets.splice(packetsToRemove[i], 1);
        }
    }

    draw() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.fillStyle = '#f8f9fa'; // Match log background slightly
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);


        // --- Draw Connections ---
        this.ctx.lineWidth = 3;
        this.ctx.strokeStyle = this.getConnectionColor(this.currentIPCType); // Use current global type for the line
        this.ctx.lineCap = 'round';

        this.connections.forEach(conn => {
            this.ctx.beginPath();
            // Draw a single line between connected processes
            this.ctx.moveTo(conn.processA.x, conn.processA.y);
            this.ctx.lineTo(conn.processB.x, conn.processB.y);
            this.ctx.stroke();
            // Optionally draw arrows or labels based on conn.type if needed later
        });

        // --- Draw Processes ---
        this.processes.forEach(process => {
            this.ctx.beginPath();
            // Use a flashing effect if the process recently received a message
            this.ctx.fillStyle = process.flashUntil && Date.now() < process.flashUntil ? '#2ecc71' : '#3498db'; // Green flash, else blue
            this.ctx.arc(process.x, process.y, process.radius, 0, Math.PI * 2);
            this.ctx.fill();

            this.ctx.strokeStyle = '#2980b9'; // Darker blue border
            this.ctx.lineWidth = 2;
            this.ctx.stroke();

            // Draw process name
            this.ctx.fillStyle = 'white';
            this.ctx.font = 'bold 14px sans-serif';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(process.name, process.x, process.y);
        });

        // --- Draw Data Packets ---
        this.dataPackets.forEach(packet => {
            this.ctx.beginPath();
            // Color packet based on the IPC type it was sent with?
            // this.ctx.fillStyle = this.getConnectionColor(packet.ipcType);
            this.ctx.fillStyle = '#f1c40f'; // Yellow packet
            this.ctx.arc(packet.x, packet.y, 8, 0, Math.PI * 2); // Slightly larger packet
            this.ctx.fill();
            this.ctx.strokeStyle = '#f39c12'; // Darker yellow border
            this.ctx.lineWidth = 1;
            this.ctx.stroke();

             // Optional: Draw message snippet with packet (can get cluttered)
            // this.ctx.fillStyle = 'black';
            // this.ctx.font = '10px sans-serif';
            // this.ctx.fillText(packet.message.substring(0, 10), packet.x + 10, packet.y - 10);
        });
    }

     flashProcess(processId, duration = 500) {
        const process = this.processes.find(p => p.id === processId);
        if (process) {
            process.flashUntil = Date.now() + duration;
            // No need to redraw immediately, the animation loop will handle it
        }
    }

    // --- Helpers ---

    getConnectionColor(type) {
        switch (type) {
            case 'pipe': return '#3498db'; // Blue
            case 'messageQueue': return '#e67e22'; // Orange
            case 'sharedMemory': return '#9b59b6'; // Purple
            default: return '#2c3e50'; // Dark Gray/Blue
        }
    }

    getIPCTypeName(type) {
         switch (type) {
            case 'pipe': return 'Named Pipe';
            case 'messageQueue': return 'Message Queue';
            case 'sharedMemory': return 'Shared Memory';
            default: return 'Unknown';
        }
    }

    log(message, type = 'info') {
        const logContent = this.logContent; // Use cached element
        const entry = document.createElement('div');
        entry.className = `log-entry log-${type}`; // Add type class for potential styling
        entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        // Add ARIA attributes for live region politeness if not already on logContent
        logContent.setAttribute('aria-relevant', 'additions text');
        logContent.setAttribute('aria-live', 'polite');

        logContent.appendChild(entry);
        // Scroll to the bottom
        logContent.scrollTop = logContent.scrollHeight;
    }

     // --- Dynamic Dropdown Updates (Optional but nice UX) ---

    updateTargetProcessOptions() {
        const sourceId = parseInt(this.sourceProcessSelect.value);
        const currentTargetId = parseInt(this.targetProcessSelect.value);
        let newTargetId = null;

        // Clear existing target options
        this.targetProcessSelect.innerHTML = '';

        // Add available processes excluding the selected source
        this.processes.forEach(p => {
            if (p.id !== sourceId) {
                const option = document.createElement('option');
                option.value = p.id;
                option.textContent = p.name;
                this.targetProcessSelect.appendChild(option);
                // Try to keep the previously selected target if it's still valid
                 if (p.id === currentTargetId) {
                     newTargetId = currentTargetId;
                 }
            }
        });

         // If the previously selected target is no longer valid (because it was the source),
         // select the first available option.
         if (newTargetId !== null) {
             this.targetProcessSelect.value = newTargetId;
         } else if (this.targetProcessSelect.options.length > 0) {
             this.targetProcessSelect.value = this.targetProcessSelect.options[0].value;
         }
    }

     updateSourceProcessOptions() {
        // Similar logic if you want source dropdown to update when target changes
        // (less common interaction, but possible)
        const targetId = parseInt(this.targetProcessSelect.value);
        const currentSourceId = parseInt(this.sourceProcessSelect.value);
         let newSourceId = null;

        this.sourceProcessSelect.innerHTML = '';

        this.processes.forEach(p => {
            if (p.id !== targetId) {
                 const option = document.createElement('option');
                option.value = p.id;
                option.textContent = p.name;
                this.sourceProcessSelect.appendChild(option);
                 if (p.id === currentSourceId) {
                     newSourceId = currentSourceId;
                 }
            }
        });

         if (newSourceId !== null) {
             this.sourceProcessSelect.value = newSourceId;
         } else if (this.sourceProcessSelect.options.length > 0) {
             this.sourceProcessSelect.value = this.sourceProcessSelect.options[0].value;
         }
    }
}

// Initialize the visualization when the DOM is ready
window.addEventListener('DOMContentLoaded', () => {
    new IPCVisualizer();
});