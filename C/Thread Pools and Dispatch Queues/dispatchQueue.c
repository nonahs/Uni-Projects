#include "dispatchQueue.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <pthread.h>
#include <sys/sysinfo.h>
#include <semaphore.h>


void add_to_list(node_t* head, task_t *task) {
	node_t *new_node;
	new_node = (node_t *)malloc(sizeof (node_t));
	new_node->task = task;
	new_node->next = head;
	new_node->prev = head->prev;
	head->prev->next = new_node;
	head->prev = new_node;
}

void *task_runner(void *thread_pool) {
	dispatch_queue_t *pool = (dispatch_queue_t *)thread_pool;
	task_t *my_task;
	
	while (1) {
		//printf("LOCKING\n");
		pthread_mutex_lock(&(pool->queue_lock)); //lock the threads
		while (pool->task_amount == 0) {
			if (pool->shutdown) {
				pthread_mutex_unlock(&(pool->queue_lock));
				pthread_exit(NULL);
			}
			pthread_mutex_unlock(&(pool->queue_lock));
			pthread_cond_wait(&(pool->notify), &(pool->queue_lock));
			if (pool->shutdown) {
				pthread_mutex_unlock(&(pool->queue_lock));
				pthread_exit(NULL);
			}
		}
		
		//printf("PAST LOCK\n");
		sem_wait(&(pool->thread_semaphore));
		my_task = &pool->task_queue[pool->head]; //get the first task
		pool->task_amount -= 1;
		//printf("RUNNING task name %s\n", my_task->name);
		
		pool->head = (pool->head +1);
		sem_post(&(pool->thread_semaphore));
		
		pthread_mutex_unlock(&(pool->queue_lock));
		my_task->work(my_task->params); //Execute the task
		//printf("DONE\n");
		
		pool->shutdown = 1;
		sem_post(&(pool->thread_semaphore));
		pthread_cond_signal(&(pool->notify)); //signal to waiting threads
		pthread_mutex_unlock(&(pool->queue_lock));
		
		pool->shutdown = 1;
	}
	
}

dispatch_queue_t *dispatch_queue_create(queue_type_t queueType) {
	/*
	Creates a dispatch queue setting up any associated threads and a linked list to be used by
	the added tasks. The queueType is either CONCURRENT or SERIAL.
	Returns: A pointer to the created dispatch queue.
	*/
	int cores = sysconf(_SC_NPROCESSORS_ONLN); //num of threads
	sem_t semaphore;
	
	dispatch_queue_t *thread_pool;
	thread_pool = (dispatch_queue_t *)malloc(sizeof(dispatch_queue_t));
	thread_pool->thread_semaphore = semaphore;
	sem_init(&(thread_pool->thread_semaphore), 0, 1); //initalize semaphore

	thread_pool->queue_type = queueType;
	if (thread_pool->queue_type == 1) cores = 1;
	thread_pool->queue_size = 12;
	thread_pool->head = 0;
	thread_pool->tail = 0;
	thread_pool->shutdown = 0;
	thread_pool->task_amount = 0;
	thread_pool->current = 0;
	thread_pool->threads = (pthread_t *)malloc(sizeof(pthread_t) * cores); //create the threads
	thread_pool->task_queue = (task_t *)malloc(sizeof(task_t) * 12);  //create the queue
	
	pthread_mutex_init(&(thread_pool->queue_lock), NULL); //initalize locks
	pthread_cond_init(&(thread_pool->notify), NULL);
	
	int i;
	for (i = 0; i < cores; i++) {
		pthread_create(&(thread_pool->threads[i]), NULL, task_runner, thread_pool);
	}
	return thread_pool;

}

void dispatch_queue_destroy(dispatch_queue_t *queue) {
	/*Destroys the dispatch queue queue. All allocated memory and resources such as semaphores are
	released and returned.
	*/
	pthread_cond_signal(&(queue->notify)); //notify any waiting threads
	queue->shutdown = 1;
	
	free(queue);
}

task_t *task_create(void (* work)(void *), void *params, char* name) {
	/*
	Creates a task. work is the function to be called when the task is executed, param is a pointer to
	either a structure which holds all of the parameters for the work function to execute with or a single
	parameter which the work function uses. If it is a single parameter it must either be a pointer or
	something which can be cast to or from a pointer. The name is a string of up to 63 characters. This
	is useful for debugging purposes.
	Returns: A pointer to the created task.
	*/
	//printf("Creating task %s\n", name);
	task_t *task = (task_t *)malloc(sizeof (task_t));
    task->work = work; // (*task).work = work;
    task->params = params;
    strcpy(task->name, name);
	//printf("Task name %s created\n", task->name);
    return task;
}

void task_destroy(task_t *task) {
	/*
	Free memory allocated to the task.
	*/
	free(task);
}

void dispatch_sync(dispatch_queue_t *queue, task_t *task) {
	/*
	Sends the task to the queue (which could be either CONCURRENT or SERIAL). This function does
	not return to the calling thread until the task has been completed.
	*/

	int next, current;
	//printf("Adding task\n");
	pthread_mutex_lock(&(queue->queue_lock)); //lock while assigning task
	current = (queue->tail);
	if (queue->queue_size == 0) {	//check if queue is empty
		queue->task_queue[queue->tail] = *task;
		queue->task_queue[queue->head] = *task;
		queue->current = queue->head;
	} else {
		next = (queue->tail +1);
		queue->task_queue[queue->tail] = *task;
		queue->current = queue->head;
		queue->tail = next;
	}
	queue->task_amount++;
	queue->current = queue->head;
	
	pthread_mutex_unlock(&queue->queue_lock);
	pthread_cond_signal(&(queue->notify));
	current = (queue->head);
	pthread_join(queue->threads[current], NULL); //wait for thread to complete
	sem_destroy(&(queue->thread_semaphore));
	queue->shutdown = 1;
	task_destroy(task);
}

void dispatch_async(dispatch_queue_t *queue, task_t *task) {
	/*
	Sends the task to the queue (which could be either CONCURRENT or SERIAL). This function
	returns immediately, the task will be dispatched sometime in the future.
	*/
	int next, current;
	//printf("Adding task\n");
	current = (queue->tail);
	pthread_mutex_lock(&(queue->queue_lock)); //lock threads
	
	queue->task_queue[queue->tail] = *task; //assign task
	next = (queue->tail +1);
	queue->tail = next;
	//printf("TAIL: %d\n", queue->tail);
	
	queue->task_amount++;
	//printf("Task amount %d\n", queue->task_amount);
	//printf("Added task\n");
	pthread_cond_signal(&(queue->notify));
	pthread_mutex_unlock(&queue->queue_lock);
	task_destroy(task);
}

void dispatch_queue_wait(dispatch_queue_t *queue) {
	/*
	Waits (blocks) until all tasks on the queue have completed. If new tasks are added to the queue
	after this is called they are ignored.
	*/
	int current;
	current = (queue->current);
	//printf("current %i\n", current);
	pthread_join(queue->threads[current], NULL);
}
