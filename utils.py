import numpy as np


def whiten(batch, rms=0.038021):
    """This function whitens a batch so each sample has 0 mean and the same root mean square amplitude i.e. volume."""
    if len(batch.shape) != 3:
        raise(ValueError, 'Input must be a 3D array of shape (n_segments, n_timesteps, 1).')

    # Subtract mean
    sample_wise_mean = batch.mean(axis=1)
    whitened_batch = batch - np.tile(sample_wise_mean, (1, 1, batch.shape[1])).transpose((1, 2, 0))

    # Divide through
    sample_wise_rescaling = rms / np.sqrt(np.power(batch, 2).mean())
    whitened_batch = whitened_batch * np.tile(sample_wise_rescaling, (1, 1, batch.shape[1])).transpose((1, 2, 0))

    return whitened_batch


def evaluate_siamese_network(siamese, dataset, preprocessor, num_tasks, n, k):
    """Evaluate a siamese network on k-way, n-shot classification tasks generated from a particular dataset."""
    # Currently assumes 1 shot classification in evaluation loop
    if n != 1:
        raise NotImplementedError

    # TODO: Faster/multiprocessing creation of tasks
    n_correct = 0
    for i_eval in range(num_tasks):
        query_sample, support_set_samples = dataset.build_n_shot_task(k, n)

        input_1 = np.stack([query_sample[0]] * k)[:, :, np.newaxis]
        input_2 = support_set_samples[0][:, :, np.newaxis]

        # Perform preprocessing
        # Pass an empty list to the labels parameter as preprocessor functions on batches not samples
        ([input_1, input_2], _) = preprocessor(([input_1, input_2], []))

        pred = siamese.predict([input_1, input_2])

        if np.argmin(pred[:, 0]) == 0:
            # 0 is the correct result as by the function definition
            n_correct += 1

    return n_correct
