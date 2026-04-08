const taskInput = document.getElementById('taskInput');
const addBtn = document.getElementById('addBtn');
const taskList = document.getElementById('taskList');
const emptyHint = document.getElementById('emptyHint');
const clearCompletedBtn = document.getElementById('clearCompletedBtn');
const clearAllBtn = document.getElementById('clearAllBtn');
const taskTemplate = document.getElementById('taskTemplate');
const todayLabel = document.getElementById('todayLabel');

const storageKey = 'daily-planner-tasks';

function getTodayText() {
  const formatter = new Intl.DateTimeFormat('zh-TW', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
  return `今天是 ${formatter.format(new Date())}`;
}

function loadTasks() {
  try {
    return JSON.parse(localStorage.getItem(storageKey)) ?? [];
  } catch {
    return [];
  }
}

function saveTasks(tasks) {
  localStorage.setItem(storageKey, JSON.stringify(tasks));
}

let tasks = loadTasks();

function toggleEmptyHint() {
  emptyHint.hidden = tasks.length > 0;
}

function renderTasks() {
  taskList.innerHTML = '';

  tasks.forEach((task) => {
    const node = taskTemplate.content.cloneNode(true);
    const item = node.querySelector('.task-item');
    const checkbox = node.querySelector('.task-checkbox');
    const text = node.querySelector('.task-text');
    const deleteBtn = node.querySelector('.delete-btn');

    item.dataset.id = task.id;
    checkbox.checked = task.done;
    text.textContent = task.text;
    text.classList.toggle('done', task.done);

    checkbox.addEventListener('change', () => {
      tasks = tasks.map((t) =>
        t.id === task.id ? { ...t, done: checkbox.checked } : t
      );
      saveTasks(tasks);
      renderTasks();
    });

    deleteBtn.addEventListener('click', () => {
      tasks = tasks.filter((t) => t.id !== task.id);
      saveTasks(tasks);
      renderTasks();
    });

    taskList.appendChild(node);
  });

  toggleEmptyHint();
}

function addTask() {
  const text = taskInput.value.trim();
  if (!text) {
    taskInput.focus();
    return;
  }

  tasks.unshift({
    id: crypto.randomUUID(),
    text,
    done: false,
  });

  saveTasks(tasks);
  taskInput.value = '';
  renderTasks();
  taskInput.focus();
}

addBtn.addEventListener('click', addTask);
taskInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') addTask();
});

clearCompletedBtn.addEventListener('click', () => {
  tasks = tasks.filter((task) => !task.done);
  saveTasks(tasks);
  renderTasks();
});

clearAllBtn.addEventListener('click', () => {
  if (!tasks.length) return;

  const shouldClear = window.confirm('確定要清空今天所有行程嗎？');
  if (!shouldClear) return;

  tasks = [];
  saveTasks(tasks);
  renderTasks();
});

todayLabel.textContent = getTodayText();
renderTasks();
